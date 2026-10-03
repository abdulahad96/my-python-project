#!/usr/bin/env python3
"""
Composite Scoring Algorithm for Tutor Ranking

This script implements a comprehensive scoring system that combines:
1. Skills Match (Jaccard similarity)
2. Experience Proximity (Gaussian scoring)
3. Rating (normalized to [0,1])

Final score: score = 0.5 * skills + 0.3 * exp + 0.2 * rating
"""

import pandas as pd
import numpy as np
import re
from typing import Set, Dict, List, Tuple, Optional


class TutorScoringSystem:
    """A comprehensive scoring system for tutor ranking"""
    
    def __init__(self, sigma: float = 2.0, default_weights: Dict[str, float] = None):
        """
        Initialize the scoring system
        
        Args:
            sigma: Standard deviation for Gaussian experience scoring
            default_weights: Default weights for composite scoring
        """
        self.sigma = sigma
        self.default_weights = default_weights or {
            'skills': 0.5, 
            'experience': 0.3, 
            'rating': 0.2
        }
    
    def jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """
        Calculate Jaccard similarity between two sets
        
        Formula: |A ∩ B| / |A ∪ B|
        
        Args:
            set1: First set of skills
            set2: Second set of skills
            
        Returns:
            Jaccard similarity score between 0 and 1
        """
        if not set1 and not set2:
            return 1.0  # Both empty sets are identical
        if not set1 or not set2:
            return 0.0  # One empty, one not
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def gaussian_experience_score(self, tutor_years: float, target_years: float) -> float:
        """
        Calculate Gaussian experience proximity score
        
        Formula: exp_score = exp(-(y - t)² / (2σ²))
        
        Args:
            tutor_years: Tutor's years of experience
            target_years: Target years of experience
            
        Returns:
            Gaussian proximity score between 0 and 1
        """
        if pd.isna(tutor_years) or pd.isna(target_years):
            return 0.0
        
        diff = tutor_years - target_years
        score = np.exp(-(diff**2) / (2 * self.sigma**2))
        return score
    
    def normalize_rating(self, rating: float) -> float:
        """
        Normalize rating to [0,1] range
        
        Args:
            rating: Original rating (assumed 0-5 scale)
            
        Returns:
            Normalized rating between 0 and 1
        """
        if pd.isna(rating):
            return 0.0
        
        # Cap at 5 and normalize to [0,1]
        normalized = min(rating, 5.0) / 5.0
        return normalized
    
    def calculate_composite_score(self, 
                                tutor_skills: Set[str], 
                                target_skills: Set[str],
                                tutor_years: float, 
                                target_years: float,
                                tutor_rating: float,
                                weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Calculate composite score for a tutor
        
        Formula: score = weights['skills'] * skills + weights['experience'] * exp + weights['rating'] * rating
        
        Args:
            tutor_skills: Tutor's skills set
            target_skills: Target skills set
            tutor_years: Tutor's years of experience
            target_years: Target years of experience
            tutor_rating: Tutor's rating
            weights: Custom weights (optional)
            
        Returns:
            Dictionary with individual and composite scores
        """
        if weights is None:
            weights = self.default_weights
        
        # Calculate individual scores
        skills_score = self.jaccard_similarity(tutor_skills, target_skills)
        exp_score = self.gaussian_experience_score(tutor_years, target_years)
        rating_score = self.normalize_rating(tutor_rating)
        
        # Calculate composite score
        composite_score = (weights['skills'] * skills_score + 
                          weights['experience'] * exp_score + 
                          weights['rating'] * rating_score)
        
        return {
            'composite_score': composite_score,
            'skills_score': skills_score,
            'exp_score': exp_score,
            'rating_score': rating_score,
            'weights_used': weights
        }
    
    def rank_tutors_skills_only(self, tutors_df: pd.DataFrame, target_skills: Set[str]) -> List[Dict]:
        """
        Rank tutors based only on skills similarity
        
        Args:
            tutors_df: DataFrame with tutor data
            target_skills: Target skills set
            
        Returns:
            List of tutors ranked by skills score
        """
        scores = []
        for _, tutor in tutors_df.iterrows():
            skills_score = self.jaccard_similarity(tutor['skills_set'], target_skills)
            scores.append({
                'tutor_id': tutor['tutor_id'],
                'name': tutor['name'],
                'skills_score': skills_score,
                'years_num': tutor['years_num'],
                'rating_norm': tutor['rating_norm'],
                'city': tutor['city']
            })
        
        return sorted(scores, key=lambda x: x['skills_score'], reverse=True)
    
    def rank_tutors_multi_factor(self, 
                               tutors_df: pd.DataFrame, 
                               target_skills: Set[str], 
                               target_years: float,
                               weights: Optional[Dict[str, float]] = None) -> List[Dict]:
        """
        Rank tutors using composite scoring
        
        Args:
            tutors_df: DataFrame with tutor data
            target_skills: Target skills set
            target_years: Target years of experience
            weights: Custom weights (optional)
            
        Returns:
            List of tutors ranked by composite score
        """
        if weights is None:
            weights = self.default_weights
        
        scores = []
        for _, tutor in tutors_df.iterrows():
            score_data = self.calculate_composite_score(
                tutor['skills_set'], target_skills,
                tutor['years_num'], target_years,
                tutor['rating_norm'], weights
            )
            scores.append({
                'tutor_id': tutor['tutor_id'],
                'name': tutor['name'],
                'composite_score': score_data['composite_score'],
                'skills_score': score_data['skills_score'],
                'exp_score': score_data['exp_score'],
                'rating_score': score_data['rating_score'],
                'years_num': tutor['years_num'],
                'rating_norm': tutor['rating_norm'],
                'city': tutor['city']
            })
        
        return sorted(scores, key=lambda x: x['composite_score'], reverse=True)
    
    def analyze_ranking_differences(self, 
                                  skills_ranking: List[Dict], 
                                  multi_ranking: List[Dict], 
                                  top_n: int = 20) -> List[Dict]:
        """
        Analyze differences between skills-only and multi-factor rankings
        
        Args:
            skills_ranking: Skills-only ranking
            multi_ranking: Multi-factor ranking
            top_n: Number of top tutors to analyze
            
        Returns:
            List of ranking differences
        """
        # Get top N tutors from each ranking
        skills_top = {tutor['tutor_id']: i for i, tutor in enumerate(skills_ranking[:top_n])}
        multi_top = {tutor['tutor_id']: i for i, tutor in enumerate(multi_ranking[:top_n])}
        
        # Find tutors that appear in both top N
        common_tutors = set(skills_top.keys()) & set(multi_top.keys())
        
        # Calculate ranking differences
        ranking_diffs = []
        for tutor_id in common_tutors:
            skills_pos = skills_top[tutor_id]
            multi_pos = multi_top[tutor_id]
            diff = skills_pos - multi_pos  # Positive means multi-factor ranked higher
            
            # Find tutor name
            tutor_name = next(t['name'] for t in skills_ranking if t['tutor_id'] == tutor_id)
            
            ranking_diffs.append({
                'tutor_id': tutor_id,
                'name': tutor_name,
                'skills_position': skills_pos + 1,
                'multi_position': multi_pos + 1,
                'position_diff': diff,
                'improved_in_multi': diff > 0
            })
        
        return ranking_diffs
    
    def test_weight_combinations(self, 
                               tutors_df: pd.DataFrame, 
                               target_skills: Set[str], 
                               target_years: float) -> Dict[str, Dict]:
        """
        Test different weight combinations to see their impact
        
        Args:
            tutors_df: DataFrame with tutor data
            target_skills: Target skills set
            target_years: Target years of experience
            
        Returns:
            Dictionary with results for each weight configuration
        """
        weight_combinations = [
            {'skills': 0.5, 'experience': 0.3, 'rating': 0.2},  # Default
            {'skills': 0.7, 'experience': 0.2, 'rating': 0.1},  # Skills-heavy
            {'skills': 0.3, 'experience': 0.5, 'rating': 0.2},  # Experience-heavy
            {'skills': 0.3, 'experience': 0.2, 'rating': 0.5},  # Rating-heavy
            {'skills': 0.4, 'experience': 0.4, 'rating': 0.2},  # Balanced skills/exp
            {'skills': 0.6, 'experience': 0.1, 'rating': 0.3},  # Skills + rating
        ]
        
        results = {}
        config_names = [
            "Default", "Skills-Heavy", "Experience-Heavy", 
            "Rating-Heavy", "Balanced S/E", "Skills+Rating"
        ]
        
        for i, weights in enumerate(weight_combinations):
            ranking = self.rank_tutors_multi_factor(tutors_df, target_skills, target_years, weights)
            results[config_names[i]] = {
                'weights': weights,
                'top_5': ranking[:5],
                'top_5_names': [t['name'] for t in ranking[:5]]
            }
        
        return results


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare the tutor data for scoring
    
    Args:
        df: Raw tutor DataFrame
        
    Returns:
        Cleaned DataFrame with extracted features
    """
    df_clean = df.copy()
    
    # Clean years_experience
    def clean_years_experience(value):
        if pd.isna(value):
            return np.nan
        value_str = str(value).strip()
        if value_str in ['seven', 'seven']:
            return 7
        elif value_str in ['five', 'five']:
            return 5
        elif value_str in ['three', 'three']:
            return 3
        elif value_str in ['four', 'four']:
            return 4
        elif value_str in ['six', 'six']:
            return 6
        elif value_str in ['eight', 'eight']:
            return 8
        elif value_str == '—':
            return np.nan
        elif '+' in value_str:
            match = re.search(r'(\d+)\+', value_str)
            if match:
                return int(match.group(1))
        elif 'years' in value_str.lower():
            match = re.search(r'(\d+)\s*years?', value_str.lower())
            if match:
                return int(match.group(1))
        elif 'year' in value_str.lower():
            match = re.search(r'(\d+)\s*year', value_str.lower())
            if match:
                return int(match.group(1))
        else:
            try:
                return pd.to_numeric(value_str, errors='coerce')
            except:
                return np.nan
    
    # Clean hourly_rate
    def clean_hourly_rate(value):
        if pd.isna(value) or str(value).strip() in ['N/A', '']:
            return np.nan
        value_str = str(value).strip()
        if 'PKR' in value_str.upper():
            match = re.search(r'PKR\s*(\d+)', value_str.upper())
            if match:
                return float(match.group(1))
        if '$' in value_str:
            match = re.search(r'(\d+)\s*\$', value_str)
            if match:
                return float(match.group(1))
            match = re.search(r'\$\s*(\d+)', value_str)
            if match:
                return float(match.group(1))
        if 'usd' in value_str.lower():
            match = re.search(r'(\d+)\s*usd', value_str.lower())
            if match:
                return float(match.group(1))
        if ',' in value_str and '-' in value_str:
            match = re.search(r'(\d+)', value_str)
            if match:
                return float(match.group(1))
        match = re.search(r'(\d+)', value_str)
        if match:
            return float(match.group(1))
        return np.nan
    
    # Create skills_set
    def create_skills_set(subjects_str):
        if pd.isna(subjects_str) or str(subjects_str).strip() == '':
            return set()
        subjects = [subject.strip() for subject in str(subjects_str).split(',')]
        skills = set()
        for subject in subjects:
            if subject and subject != '':
                cleaned_subject = ' '.join(subject.split()).title()
                skills.add(cleaned_subject)
        return skills
    
    # Apply cleaning
    df_clean['years_num'] = df_clean['years_experience'].apply(clean_years_experience)
    df_clean['rate_num'] = df_clean['hourly_rate'].apply(clean_hourly_rate)
    df_clean['skills_set'] = df_clean['subjects'].apply(create_skills_set)
    df_clean['rating_norm'] = df_clean['rating'].apply(lambda x: min(x, 5.0) / 5.0 if not pd.isna(x) else np.nan)
    
    return df_clean


def main():
    """Main function to demonstrate the composite scoring system"""
    
    print("=== COMPOSITE SCORING ALGORITHM DEMONSTRATION ===\n")
    
    # Load data
    try:
        df = pd.read_csv('data.csv')
        print(f"✅ Loaded {len(df)} tutors from data.csv")
    except FileNotFoundError:
        print("❌ Error: data.csv not found. Please ensure the file exists.")
        return
    
    # Clean data
    df_clean = clean_data(df)
    print(f"✅ Data cleaned and features extracted")
    print(f"   - Years range: {df_clean['years_num'].min():.0f} - {df_clean['years_num'].max():.0f}")
    print(f"   - Rate range: {df_clean['rate_num'].min():.0f} - {df_clean['rate_num'].max():.0f}")
    print(f"   - Rating range: {df_clean['rating_norm'].min():.3f} - {df_clean['rating_norm'].max():.3f}")
    print(f"   - Unique skills: {len(set().union(*df_clean['skills_set']))}")
    
    # Initialize scoring system
    scoring_system = TutorScoringSystem(sigma=2.0)
    print(f"\n✅ Scoring system initialized with σ={scoring_system.sigma}")
    
    # Test scenario: Looking for Math tutor with 5 years experience
    target_skills = {'Math'}
    target_years = 5
    
    print(f"\n=== TEST SCENARIO ===")
    print(f"Target: {target_skills} tutor with {target_years} years experience")
    
    # Test individual scoring functions
    print(f"\n1. JACCARD SIMILARITY TEST:")
    sample_skills1 = {'Math', 'Physics', 'Chemistry'}
    sample_skills2 = {'Math', 'Physics', 'Biology'}
    jaccard_score = scoring_system.jaccard_similarity(sample_skills1, sample_skills2)
    print(f"   Skills 1: {sample_skills1}")
    print(f"   Skills 2: {sample_skills2}")
    print(f"   Jaccard similarity: {jaccard_score:.3f}")
    
    print(f"\n2. GAUSSIAN EXPERIENCE SCORING TEST (σ=2):")
    print(f"   Target experience: {target_years} years")
    test_years = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for years in test_years:
        score = scoring_system.gaussian_experience_score(years, target_years)
        print(f"   Tutor {years:2d} years → Score: {score:.3f}")
    
    # Get rankings
    print(f"\n3. RANKING COMPARISON:")
    skills_only_ranking = scoring_system.rank_tutors_skills_only(df_clean, target_skills)
    multi_factor_ranking = scoring_system.rank_tutors_multi_factor(df_clean, target_skills, target_years)
    
    print(f"\n   Top 10 tutors (Skills-Only Ranking):")
    for i, tutor in enumerate(skills_only_ranking[:10]):
        print(f"   {i+1:2d}. {tutor['name']:20s} Skills={tutor['skills_score']:.3f} "
              f"Years={tutor['years_num']:2.0f} Rating={tutor['rating_norm']:.2f}")
    
    print(f"\n   Top 10 tutors (Multi-Factor Ranking):")
    for i, tutor in enumerate(multi_factor_ranking[:10]):
        print(f"   {i+1:2d}. {tutor['name']:20s} Composite={tutor['composite_score']:.3f} "
              f"(S={tutor['skills_score']:.2f}, E={tutor['exp_score']:.2f}, R={tutor['rating_score']:.2f}) "
              f"Years={tutor['years_num']:2.0f}")
    
    # Analyze ranking differences
    print(f"\n4. RANKING ANALYSIS:")
    ranking_diffs = scoring_system.analyze_ranking_differences(skills_only_ranking, multi_factor_ranking)
    
    skills_top_10_ids = {t['tutor_id'] for t in skills_only_ranking[:10]}
    multi_top_10_ids = {t['tutor_id'] for t in multi_factor_ranking[:10]}
    overlap = len(skills_top_10_ids & multi_top_10_ids)
    
    improved_count = sum(1 for d in ranking_diffs if d['improved_in_multi'])
    
    print(f"   - Top 10 overlap: {overlap}/10 tutors ({overlap*10}%)")
    print(f"   - Tutors improved in multi-factor: {improved_count}/{len(ranking_diffs)}")
    print(f"   - Average position change: {np.mean([d['position_diff'] for d in ranking_diffs]):.1f}")
    
    # Test weight combinations
    print(f"\n5. WEIGHT SENSITIVITY ANALYSIS:")
    weight_results = scoring_system.test_weight_combinations(df_clean, target_skills, target_years)
    
    for config_name, result in weight_results.items():
        weights = result['weights']
        top_3 = result['top_5_names'][:3]
        print(f"   {config_name:15s} (S:{weights['skills']:.1f} E:{weights['experience']:.1f} R:{weights['rating']:.1f}): {top_3}")
    
    # Reflection
    print(f"\n=== REFLECTION & RECOMMENDATIONS ===")
    print(f"\n1. DOES ADDING EXPERIENCE/RATING IMPROVE RANKING VS SKILLS-ONLY?")
    print(f"   ✅ YES - Multi-factor ranking provides significant improvements:")
    print(f"   ✓ Considers tutor quality (rating) beyond just subject match")
    print(f"   ✓ Balances experience level with student needs")
    print(f"   ✓ Provides more nuanced ranking for similar skill matches")
    print(f"   ✓ Reduces bias toward tutors with many skills but poor quality")
    
    print(f"\n2. SHOULD WEIGHTS BE FIXED OR USER-TUNABLE?")
    print(f"   🎛️  RECOMMENDATION: User-tunable with smart defaults")
    print(f"   📊 DEFAULT WEIGHTS: Skills=0.5, Experience=0.3, Rating=0.2")
    print(f"   🎛️  USER CONTROLS: Slider interface for weight adjustment")
    print(f"   📈 PRESET PROFILES: 'Quality Focus', 'Budget Focus', 'Experience Focus'")
    print(f"   🔄 REAL-TIME UPDATES: Rankings update as weights change")
    print(f"   💾 SAVE PREFERENCES: Remember user's preferred weight settings")
    
    print(f"\n✅ Composite scoring algorithm demonstration complete!")


if __name__ == "__main__":
    main()

