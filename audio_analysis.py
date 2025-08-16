import whisper
import numpy as np
import language_tool_python
from pydub import AudioSegment
import os
import time
import json
import torch
from textblob import TextBlob
import re
import string
import gc

# GPU memory management for Hugging Face Spaces
if torch.cuda.is_available():
    print("CUDA is available. GPU will be used for inference.")
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Set memory fraction to avoid OOM errors
    torch.cuda.set_per_process_memory_fraction(0.8)
else:
    print("CUDA is NOT available. Running on CPU.")

def transcribe_audio(audio_path):
    """Transcribe audio using whisper (optimized for HF Spaces)"""
    try:
        # Use tiny model for faster inference and less memory usage
        model = whisper.load_model("tiny")
        
        # Move model to GPU if available
        if torch.cuda.is_available():
            model = model.cuda()
        
        result = model.transcribe(audio_path)
        
        # Clean up GPU memory
        if torch.cuda.is_available():
            del model
            torch.cuda.empty_cache()
            gc.collect()
        
        return result['text']
    except Exception as e:
        print(f"Transcription error: {e}")
        # Fallback to CPU if GPU fails
        try:
            model = whisper.load_model("tiny")
            result = model.transcribe(audio_path)
            return result['text']
        except Exception as e2:
            print(f"CPU fallback also failed: {e2}")
            return ""

def _normalize_text_for_compare(text: str) -> list:
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return [t for t in text.split() if t]

def _wer_alignment(ref_tokens, hyp_tokens):
    # Compute WER dynamic programming table and backtrack to get operations
    n, m = len(ref_tokens), len(hyp_tokens)
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    op = [[None] * (m + 1) for _ in range(n + 1)]
    # Weighted costs (stricter): substitutions/deletions penalized more than insertions
    cost_sub, cost_ins, cost_del = 1.2, 1.0, 1.2
    for i in range(1, n + 1):
        dp[i][0] = i * cost_del
        op[i][0] = 'D'
    for j in range(1, m + 1):
        dp[0][j] = j * cost_ins
        op[0][j] = 'I'
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                op[i][j] = 'E'  # equal
            else:
                # substitution, insertion, deletion
                choices = (
                    (dp[i - 1][j - 1] + cost_sub, 'S'),
                    (dp[i][j - 1] + cost_ins, 'I'),
                    (dp[i - 1][j] + cost_del, 'D'),
                )
                dp[i][j], op[i][j] = min(choices, key=lambda x: x[0])
    # Backtrack
    i, j = n, m
    edits = []  # list of tuples (op, ref_token or None, hyp_token or None)
    while i > 0 or j > 0:
        cur_op = op[i][j]
        if cur_op == 'E':
            edits.append(('E', ref_tokens[i - 1], hyp_tokens[j - 1]))
            i -= 1
            j -= 1
        elif cur_op == 'S':
            edits.append(('S', ref_tokens[i - 1], hyp_tokens[j - 1]))
            i -= 1
            j -= 1
        elif cur_op == 'I':
            edits.append(('I', None, hyp_tokens[j - 1]))
            j -= 1
        elif cur_op == 'D':
            edits.append(('D', ref_tokens[i - 1], None))
            i -= 1
        else:
            break
    edits.reverse()
    subs = [(r, h) for t, r, h in edits if t == 'S']
    ins = [h for t, r, h in edits if t == 'I']
    dels = [r for t, r, h in edits if t == 'D']
    wer = dp[n][m] / max(1, float(n))
    return wer, subs, ins, dels

def compare_transcript_to_reference(reference_text: str, hypothesis_text: str):
    ref = _normalize_text_for_compare(reference_text)
    hyp = _normalize_text_for_compare(hypothesis_text)
    wer, subs, ins, dels = _wer_alignment(ref, hyp)
    # Count-based scoring so that 2 substitutions => 90 exactly when no other errors
    substitution_penalty = 5.0 * len(subs)
    insertion_penalty = 2.0 * len(ins)
    deletion_penalty = 3.0 * len(dels)
    raw_score = 100.0 - substitution_penalty - insertion_penalty - deletion_penalty
    similarity_score = round(max(0.0, min(100.0, raw_score)), 1)
    summary = []
    if wer == 0:
        summary.append("Perfect match with the provided script")
    else:
        if subs:
            summary.append(f"{len(subs)} substitutions detected")
        if ins:
            summary.append(f"{len(ins)} extra words spoken (insertions)")
        if dels:
            summary.append(f"{len(dels)} missing words (deletions)")
    # Provide a few examples
    examples = []
    for r, h in subs[:3]:
        examples.append(f"substituted '{r}' with '{h}'")
    for w in dels[:2]:
        examples.append(f"missed '{w}'")
    for w in ins[:2]:
        examples.append(f"added '{w}'")
    if examples:
        summary.append("Examples: " + "; ".join(examples))
    result = {
        "score": similarity_score,
        "errors": {
            "substitutions": [{"from": r, "to": h} for (r, h) in subs],
            "insertions": ins,
            "deletions": dels
        },
        "summary": summary + [
            f"Substitution penalty: -{int(substitution_penalty)}",
            f"Insertion penalty: -{int(insertion_penalty)}",
            f"Deletion penalty: -{int(deletion_penalty)}"
        ]
    }
    return result

def analyze_fluency_audio_only(audio_path):
    """Analyze fluency using only audio characteristics - no transcription needed"""
    # Use pydub to get audio duration and samples
    audio = AudioSegment.from_file(audio_path)
    duration = len(audio) / 1000.0  # Convert to seconds
    
    # Get audio samples
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        # Use average of both channels
        samples = np.mean(samples, axis=1)
    
    # Convert to float and normalize safely
    samples = samples.astype(np.float32)
    max_abs = float(np.max(np.abs(samples))) if samples.size > 0 else 0.0
    if max_abs > 0.0:
        samples = samples / max_abs
    else:
        # Completely silent audio; return minimal metrics
        return {
            "duration_sec": duration,
            "speech_activity_ratio": 0.0,
            "speech_rate": 0.0,
            "rhythm_consistency": 0.0,
            "energy_variation": 0.0,
            "pause_count": 0,
            "pause_frequency": 0.0,
            "estimated_wpm": 0,
            "speech_bursts": 0
        }
    
    # Calculate audio energy over time
    frame_length = int(0.025 * audio.frame_rate)  # 25ms frames
    hop_length = int(0.010 * audio.frame_rate)    # 10ms hop
    
    energy = []
    for i in range(0, max(0, len(samples) - frame_length), hop_length):
        frame = samples[i:i + frame_length]
        if frame.size == 0:
            continue
        energy.append(float(np.sqrt(np.mean(frame**2))))
    energy = np.array(energy, dtype=np.float32)
    if energy.size == 0:
        # Not enough frames to analyze
        return {
            "duration_sec": duration,
            "speech_activity_ratio": 0.0,
            "speech_rate": 0.0,
            "rhythm_consistency": 0.0,
            "energy_variation": 0.0,
            "pause_count": 0,
            "pause_frequency": 0.0,
            "estimated_wpm": 0,
            "speech_bursts": 0
        }
    # Smooth energy with a small moving average to reduce spikes/noise
    if energy.size >= 5:
        kernel = np.ones(5, dtype=np.float32) / 5.0
        energy = np.convolve(energy, kernel, mode='same')
    
    # Analyze speech activity
    # Find speech segments (high energy) vs silence (low energy)
    # Dynamic threshold: blend percentile and mean-based
    energy_threshold = max(np.percentile(energy, 30), float(np.mean(energy)) * 0.6)
    speech_segments = energy > energy_threshold
    
    # Calculate speech activity ratio
    speech_activity_ratio = np.sum(speech_segments) / len(speech_segments)
    
    # Find speech rate patterns
    # Count speech bursts (consecutive speech frames)
    speech_bursts = []
    in_speech = False
    burst_start = 0
    
    for i, is_speech in enumerate(speech_segments):
        if is_speech and not in_speech:
            in_speech = True
            burst_start = i
        elif not is_speech and in_speech:
            burst_duration = (i - burst_start) * hop_length / audio.frame_rate
            if burst_duration > 0.1:  # Only count bursts longer than 100ms
                speech_bursts.append(burst_duration)
            in_speech = False
    
    # Calculate speech rate metrics
    total_speech_time = np.sum(speech_bursts)
    speech_rate = total_speech_time / duration if duration > 0 else 0
    
    # Analyze rhythm and flow
    if len(speech_bursts) > 1:
        # Rhythm consistency via coefficient of variation of burst durations
        durations = np.array(speech_bursts, dtype=np.float32)
        mean_dur = float(np.mean(durations))
        std_dur = float(np.std(durations))
        cv = (std_dur / mean_dur) if mean_dur > 1e-6 else 1.0
        rhythm_consistency = 1.0 / (1.0 + cv)  # Higher is more consistent
    else:
        rhythm_consistency = 0.5  # Default for very short speech
    
    # Analyze energy variation (indicates natural speech patterns)
    speech_mask_sum = int(np.sum(speech_segments))
    if speech_mask_sum > 0:
        energy_speech = energy[speech_segments]
        energy_variation = float(np.std(energy_speech))
        mean_energy_speech = float(np.mean(energy_speech))
        energy_variation_normalized = (energy_variation / mean_energy_speech) if mean_energy_speech > 1e-8 else 0.0
    else:
        energy_variation = 0.0
        energy_variation_normalized = 0.0
    
    # Find pauses and hesitations
    silence_threshold = np.percentile(energy, 15)
    silence_segments = energy < silence_threshold
    
    # Count significant pauses
    pause_count = 0
    in_pause = False
    pause_start = 0
    
    for i, is_silent in enumerate(silence_segments):
        if is_silent and not in_pause:
            in_pause = True
            pause_start = i
        elif not is_silent and in_pause:
            pause_duration = (i - pause_start) * hop_length / float(audio.frame_rate)
            if pause_duration > 0.3:  # Count pauses longer than 300ms
                pause_count += 1
            in_pause = False
    
    # Calculate pause frequency
    pause_frequency = pause_count / (duration / 60.0) if duration > 0 else 0.0
    
    # Estimate words per minute based on speech patterns
    # Average English speaker: ~150 WPM, but varies with speech rate
    estimated_wpm = int(max(0.0, speech_rate) * 150.0 * (1.0 + max(0.0, energy_variation_normalized) * 0.5))
    
    return {
        "duration_sec": duration,
        "speech_activity_ratio": speech_activity_ratio,
        "speech_rate": speech_rate,
        "rhythm_consistency": rhythm_consistency,
        "energy_variation": energy_variation_normalized,
        "pause_count": pause_count,
        "pause_frequency": pause_frequency,
        "estimated_wpm": estimated_wpm,
        "speech_bursts": len(speech_bursts)
    }

def analyze_fluency_advanced_audio(fluency_stats):
    """Advanced fluency analysis using audio-only metrics with balanced scoring"""
    duration = fluency_stats['duration_sec']
    speech_activity_ratio = fluency_stats['speech_activity_ratio']
    speech_rate = fluency_stats['speech_rate']
    rhythm_consistency = fluency_stats['rhythm_consistency']
    energy_variation = fluency_stats['energy_variation']
    pause_frequency = fluency_stats['pause_frequency']
    estimated_wpm = fluency_stats['estimated_wpm']
    speech_bursts = fluency_stats['speech_bursts']
    
    # Fluency scoring based on audio characteristics - Balanced scoring
    fluency_score = 0
    fluency_analysis = []
    
    # Speech Activity Analysis (25 points) - Reward good audio more
    if speech_activity_ratio >= 0.7:
        fluency_score += 25
        fluency_analysis.append("Excellent speech activity - good use of speaking time")
    elif speech_activity_ratio >= 0.55:
        fluency_score += 22
        fluency_analysis.append("Good speech activity - reasonable speaking time")
    elif speech_activity_ratio >= 0.4:
        fluency_score += 17
        fluency_analysis.append("Moderate speech activity - some silence")
    elif speech_activity_ratio >= 0.25:
        fluency_score += 12
        fluency_analysis.append("Low speech activity - too much silence")
    else:
        fluency_score += 6
        fluency_analysis.append("Very low speech activity - mostly silence")
    
    # Speech Rate Analysis (25 points) - Slightly wider optimal, boost good
    if 0.62 <= speech_rate <= 0.95:
        fluency_score += 25
        fluency_analysis.append("Excellent speech rate - natural and engaging pace")
    elif 0.5 <= speech_rate < 0.62 or 0.95 < speech_rate <= 1.1:
        fluency_score += 22
        fluency_analysis.append("Good speech rate - clear and understandable")
    elif 0.38 <= speech_rate < 0.5 or 1.1 < speech_rate <= 1.3:
        fluency_score += 16
        fluency_analysis.append("Moderate speech rate - could be improved")
    elif 0.25 <= speech_rate < 0.38 or 1.3 < speech_rate <= 1.5:
        fluency_score += 10
        fluency_analysis.append("Below average speech rate - needs improvement")
    else:
        fluency_score += 5
        fluency_analysis.append("Poor speech rate - significantly needs improvement")
    
    # Rhythm and Flow Analysis (25 points) - Boost mid bands
    if rhythm_consistency >= 0.7:
        fluency_score += 25
        fluency_analysis.append("Excellent rhythm consistency - smooth flow")
    elif rhythm_consistency >= 0.55:
        fluency_score += 22
        fluency_analysis.append("Good rhythm consistency - generally smooth")
    elif rhythm_consistency >= 0.4:
        fluency_score += 16
        fluency_analysis.append("Moderate rhythm - some irregularity")
    elif rhythm_consistency >= 0.25:
        fluency_score += 10
        fluency_analysis.append("Irregular rhythm - needs improvement")
    else:
        fluency_score += 5
        fluency_analysis.append("Very irregular rhythm - significant improvement needed")
    
    # Pause Analysis (25 points) - Mid bands worth a bit more
    if pause_frequency <= 3:
        fluency_score += 25
        fluency_analysis.append("Excellent pause control - minimal hesitation")
    elif pause_frequency <= 6:
        fluency_score += 21
        fluency_analysis.append("Good pause control - reasonable pauses")
    elif pause_frequency <= 9:
        fluency_score += 17
        fluency_analysis.append("Moderate pause control - some hesitation")
    elif pause_frequency <= 14:
        fluency_score += 12
        fluency_analysis.append("Frequent pauses - indicates nervousness")
    else:
        fluency_score += 6
        fluency_analysis.append("Excessive pauses - significant improvement needed")
    
    # Energy Variation Analysis (up to 10 points) - More balanced
    if 0.3 <= energy_variation <= 0.8:  # Natural variation (more realistic)
        fluency_score += 10
        fluency_analysis.append("Natural energy variation - engaging delivery")
    elif 0.15 <= energy_variation < 0.3:
        fluency_score += 7
        fluency_analysis.append("Good energy variation - expressive speech")
    elif 0.8 < energy_variation <= 1.2:
        fluency_score += 5
        fluency_analysis.append("High energy variation - very expressive")
    elif energy_variation > 1.2:
        fluency_score += 3
        fluency_analysis.append("Very high energy variation - overly dramatic")
    else:
        fluency_score += 2
        fluency_analysis.append("Low energy variation - somewhat monotone")
    
    # Duration and Content Bonus - More balanced
    if duration >= 40 and speech_bursts >= 6:  # Higher requirements
        if fluency_score >= 70:
            fluency_score += 5
            fluency_analysis.append("Sustained fluency over extended speech")
        elif fluency_score >= 50:
            fluency_score += 3
            fluency_analysis.append("Good sustained performance")
    elif duration >= 20 and speech_bursts >= 4:  # Higher requirements
        if fluency_score >= 60:
            fluency_score += 2
            fluency_analysis.append("Consistent performance")
    
    # Speech burst analysis - More balanced
    if speech_bursts >= 8:  # Higher requirement
        if rhythm_consistency >= 0.5:  # Higher requirement
            fluency_score += 2
            fluency_analysis.append("Good speech segmentation")
    elif speech_bursts <= 2:  # Penalize more
        fluency_score -= 3  # Higher penalty
        fluency_analysis.append("Limited speech segments - may indicate hesitation")
    
    # Additional guards to prevent unrealistic perfect scores (still allow good audios to score high)
    quality_flags = [
        speech_activity_ratio >= 0.7,
        0.65 <= speech_rate <= 0.9,
        rhythm_consistency >= 0.7,
        pause_frequency <= 3,
        0.3 <= energy_variation <= 0.8,
        duration >= 20.0,
    ]
    num_flags = sum(1 for x in quality_flags if x)
    if num_flags < 2:
        fluency_score = min(fluency_score, 70)
    elif num_flags < 3:
        fluency_score = min(fluency_score, 85)
    elif num_flags < 4:
        fluency_score = min(fluency_score, 95)
    # Penalize clearly poor signals
    if speech_activity_ratio < 0.2 or speech_bursts <= 1:
        fluency_score = min(fluency_score, 40)
        fluency_analysis.append("Very limited speech activity detected")
    if duration < 8:
        fluency_score = min(fluency_score, 70)
        fluency_analysis.append("Short recording limits fluency assessment confidence")
    
    # Cap the score at 100
    fluency_score = min(100, max(0, fluency_score))
    
    return {
        "score": fluency_score,
        "analysis": fluency_analysis,
        "metrics": {
            "speech_activity_ratio": speech_activity_ratio,
            "speech_rate": speech_rate,
            "rhythm_consistency": rhythm_consistency,
            "pause_frequency": pause_frequency,
            "estimated_wpm": estimated_wpm,
            "energy_variation": energy_variation
        }
    }

def analyze_grammar_advanced(text):
    """Advanced grammar analysis using multiple tools"""
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    
    # TextBlob for additional analysis
    blob = TextBlob(text)
    
    grammar_score = 100  # Start with 100 instead of 50
    grammar_analysis = []
    
    # Error count analysis - More lenient
    num_errors = len(matches)
    if num_errors == 0:
        grammar_analysis.append("Excellent grammar - no errors detected")
    elif num_errors <= 3:  # Increased from 2
        grammar_score -= 6  # Reduced penalty (doubled from 3)
        grammar_analysis.append("Good grammar with minor errors")
    elif num_errors <= 6:  # Increased from 5
        grammar_score -= 12  # Reduced penalty (doubled from 6)
        grammar_analysis.append("Moderate grammar issues")
    elif num_errors <= 12:  # Increased from 10
        grammar_score -= 24  # Reduced penalty (doubled from 12)
        grammar_analysis.append("Significant grammar problems")
    else:
        grammar_score -= 40  # Reduced penalty (doubled from 20)
        grammar_analysis.append("Major grammar issues need attention")
    
    # Sentence structure analysis
    sentences = blob.sentences
    avg_sentence_length = np.mean([len(s.words) for s in sentences]) if sentences else 0
    
    if 8 <= avg_sentence_length <= 25:  # Expanded from 10-20
        grammar_analysis.append("Good sentence structure and variety")
    elif avg_sentence_length < 8:
        grammar_analysis.append("Sentences are too short - consider combining ideas")
    else:
        grammar_analysis.append("Sentences are quite long - consider breaking them up")
    
    # Specific error types
    error_types = {}
    for match in matches:
        error_type = match.ruleId
        if error_type not in error_types:
            error_types[error_type] = 0
        error_types[error_type] += 1
    
    if error_types:
        most_common_error = max(error_types, key=error_types.get)
        grammar_analysis.append(f"Most common error: {most_common_error}")
    
    return {
        "score": grammar_score,
        "analysis": grammar_analysis,
        "errors": [match.message for match in matches],
        "error_count": num_errors
    }

def analyze_professionalism(text):
    """Analyze professionalism based on language use"""
    professionalism_score = 50
    professionalism_analysis = []
    
    # Check for informal language - More lenient
    informal_words = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'literally']
    informal_count = sum(text.lower().count(word) for word in informal_words)
    
    if informal_count == 0:
        professionalism_score += 10
        professionalism_analysis.append("Excellent professional language - no filler words")
    elif informal_count <= 5:  # Increased from 3
        professionalism_score += 5
        professionalism_analysis.append("Good professional language with minimal filler words")
    elif informal_count <= 10:  # Increased from 6
        professionalism_analysis.append("Moderate use of filler words - could be more professional")
    else:
        professionalism_score -= 5  # Reduced penalty
        professionalism_analysis.append("Excessive use of filler words - needs improvement")
    
    # Check for confident language - More lenient
    confident_phrases = ['i believe', 'i think', 'i feel', 'maybe', 'perhaps', 'might']
    confident_count = sum(text.lower().count(phrase) for phrase in confident_phrases)
    
    if confident_count <= 4:  # Increased from 2
        professionalism_score += 10
        professionalism_analysis.append("Confident and assertive communication style")
    elif confident_count <= 8:  # Increased from 5
        professionalism_score += 5
        professionalism_analysis.append("Generally confident with some hedging")
    else:
        professionalism_score -= 3  # Reduced penalty
        professionalism_analysis.append("Overuse of hedging language - be more confident")
    
    # Check vocabulary sophistication
    words = text.lower().split()
    unique_words = len(set(words))
    total_words = len(words)
    vocabulary_richness = unique_words / total_words if total_words > 0 else 0
    
    if vocabulary_richness >= 0.6:  # Reduced from 0.7
        professionalism_score += 10
        professionalism_analysis.append("Excellent vocabulary diversity")
    elif vocabulary_richness >= 0.4:  # Reduced from 0.5
        professionalism_score += 5
        professionalism_analysis.append("Good vocabulary diversity")
    else:
        professionalism_score -= 3  # Reduced penalty
        professionalism_analysis.append("Limited vocabulary - consider expanding word choice")
    
    return {
        "score": min(100, max(0, professionalism_score)),
        "analysis": professionalism_analysis,
        "metrics": {
            "informal_words": informal_count,
            "confident_phrases": confident_count,
            "vocabulary_richness": vocabulary_richness
        }
    }

def calculate_overall_score(fluency_score, grammar_score, professionalism_score):
    """Calculate overall score with weighted components: 50% fluency, 30% grammar, 20% professionalism"""
    weights = {
        'fluency': 0.50,      # 50% weight for fluency
        'grammar': 0.30,      # 30% weight for grammar
        'professionalism': 0.20  # 20% weight for professionalism
    }
    
    overall_score = (
        fluency_score * weights['fluency'] +
        grammar_score * weights['grammar'] +
        professionalism_score * weights['professionalism']
    )
    
    return round(min(100, overall_score), 1)

def calculate_overall_score_with_similarity(fluency_score, grammar_score, similarity_score):
    """Overall score when custom text is provided: 60% similarity, 20% fluency, 20% grammar."""
    weights = {
        'similarity': 0.60,
        'fluency': 0.20,
        'grammar': 0.20,
    }
    overall_score = (
        similarity_score * weights['similarity'] +
        fluency_score * weights['fluency'] +
        grammar_score * weights['grammar']
    )
    return round(min(100, overall_score), 1)

def generate_json_report(fluency_analysis, grammar_analysis, professionalism_analysis, overall_score):
    """Generate the JSON report in the requested format"""
    
    report = {
        "overall_score": overall_score,
        "report": {
            "fluency_analysis": {
                "score": fluency_analysis["score"],
                "analysis": fluency_analysis["analysis"]
            },
            "grammar_analysis": {
                "score": grammar_analysis["score"],
                "analysis": grammar_analysis["analysis"],
                "errors": grammar_analysis["errors"],
                "error_count": grammar_analysis["error_count"]
            },
            "professionalism_analysis": {
                "score": professionalism_analysis["score"],
                "analysis": professionalism_analysis["analysis"]
            }
        }
    }
    
    return report

def generate_json_report_with_similarity(fluency_analysis, grammar_analysis, similarity_analysis, overall_score):
    """Generate report for audio + custom text case: includes similarity, fluency, grammar only."""
    return {
        "overall_score": overall_score,
        "report": {
            "fluency_analysis": {
                "score": fluency_analysis["score"],
                "analysis": fluency_analysis["analysis"]
            },
            "grammar_analysis": {
                "score": grammar_analysis["score"],
                "analysis": grammar_analysis["analysis"],
                "errors": grammar_analysis["errors"],
                "error_count": grammar_analysis["error_count"]
            },
            "similarity_analysis": similarity_analysis
        }
    }

def analyze_audio(audio_path):
    """Main function to analyze audio and return JSON result"""
    start_time = time.time()
    print("Transcribing audio...")
    transcript = transcribe_audio(audio_path)
    print("Analyzing fluency...")
    fluency_stats = analyze_fluency_audio_only(audio_path)
    print("Performing advanced analysis...")
    
    # Analyze fluency using audio metrics only
    fluency_analysis = analyze_fluency_advanced_audio(fluency_stats)
    
    # Analyze grammar and professionalism using transcribed text
    grammar_analysis = analyze_grammar_advanced(transcript)
    professionalism_analysis = analyze_professionalism(transcript)
    
    # Calculate overall score
    overall_score = calculate_overall_score(
        fluency_analysis["score"],
        grammar_analysis["score"],
        professionalism_analysis["score"]
    )
    
    # Generate JSON report (transcript not included in output)
    report = generate_json_report(
        fluency_analysis, grammar_analysis, professionalism_analysis, overall_score
    )
    
    end_time = time.time()
    print(f"Total processing time: {end_time - start_time:.2f} seconds")
    
    return report

def analyze_audio_with_text(audio_path, text):
    """Main function to analyze audio with provided text for grammar and professionalism"""
    start_time = time.time()
    print("Analyzing audio and text...")
    
    # Analyze fluency using audio-only metrics
    fluency_stats = analyze_fluency_audio_only(audio_path)
    fluency_analysis = analyze_fluency_advanced_audio(fluency_stats)

    # Transcribe audio to compare with provided custom text
    print("Transcribing audio for similarity check...")
    transcript = transcribe_audio(audio_path)

    # Analyze grammar using transcribed text (actual speech)
    grammar_analysis = analyze_grammar_advanced(transcript)
    # professionalism_analysis = analyze_professionalism(transcript) # Removed as per edit hint

    # Compare transcript with provided custom text for similarity (WER-based)
    similarity = compare_transcript_to_reference(text, transcript)

    # Calculate overall score with custom weights (similarity 0.6, fluency 0.2, grammar 0.2)
    overall_score = calculate_overall_score_with_similarity(
        fluency_analysis["score"],
        grammar_analysis["score"],
        similarity["score"]
    )

    # Generate JSON report (only similarity, fluency, grammar)
    report = generate_json_report_with_similarity(
        fluency_analysis, grammar_analysis, similarity, overall_score
    )
    
    end_time = time.time()
    print(f"Total processing time: {end_time - start_time:.2f} seconds")
    
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Audio Analysis Model for AI Recruiter")
    parser.add_argument("audio_path", help="Path to the candidate's audio file (wav/mp3)")
    parser.add_argument("--text", help="Optional transcribed text for grammar and professionalism analysis")
    args = parser.parse_args()
    
    if args.text:
        result = analyze_audio_with_text(args.audio_path, args.text)
    else:
        result = analyze_audio(args.audio_path)
    
    print(json.dumps(result, indent=2))
