#!/usr/bin/env python3
"""
Interactive Tutor Scoring Demo

This script provides an interactive demonstration of the composite scoring algorithm
where users can input their preferences and see real-time rankings.
"""

import pandas as pd
import numpy as np
import re
from composite_scoring import TutorScoringSystem, clean_data


def interactive_demo():
    """Interactive demonstration of the scoring system"""
    
    print("🎓 INTERACTIVE TUTOR SCORING DEMO")
    print("=" * 50)
    
    # Load and clean data
    try:
        df = pd.read_csv('data.csv')
        df_clean = clean_data(df)
        print(f"✅ Loaded {len(df_clean)} tutors")
    except FileNotFoundError:
        print("❌ Error: data.csv not found")
        return
    
    # Initialize scoring system
    scoring_system = TutorScoringSystem()
    
    # Get user preferences
    print("\n📝 Please enter your preferences:")
    
    # Get target skills
    print("\n1. What subjects are you looking for?")
    print("   Available subjects:", sorted(set().union(*df_clean['skills_set']))[:10], "...")
    skills_input = input("   Enter subjects (comma-separated): ").strip()
    target_skills = set(s.strip().title() for s in skills_input.split(',') if s.strip())
    
    if not target_skills:
        print("   Using default: Math")
        target_skills = {'Math'}
    
    # Get target experience
    print("\n2. How many years of experience do you prefer?")
    target_years_input = input("   Enter years (0-15): ").strip()
    try:
        target_years = float(target_years_input) if target_years_input else 5.0
    except ValueError:
        target_years = 5.0
        print("   Using default: 5 years")
    
    # Get weight preferences
    print("\n3. How important are these factors to you?")
    print("   (Enter values that sum to 1.0, e.g., 0.5, 0.3, 0.2)")
    
    skills_weight = float(input("   Skills match importance (0-1): ") or "0.5")
    exp_weight = float(input("   Experience importance (0-1): ") or "0.3")
    rating_weight = float(input("   Rating importance (0-1): ") or "0.2")
    
    # Normalize weights
    total_weight = skills_weight + exp_weight + rating_weight
    if total_weight > 0:
        skills_weight /= total_weight
        exp_weight /= total_weight
        rating_weight /= total_weight
    
    custom_weights = {
        'skills': skills_weight,
        'experience': exp_weight,
        'rating': rating_weight
    }
    
    print(f"\n🎯 Your Preferences:")
    print(f"   Target Skills: {target_skills}")
    print(f"   Target Experience: {target_years} years")
    print(f"   Weights: Skills={skills_weight:.2f}, Experience={exp_weight:.2f}, Rating={rating_weight:.2f}")
    
    # Calculate rankings
    print(f"\n📊 CALCULATING RANKINGS...")
    
    skills_only_ranking = scoring_system.rank_tutors_skills_only(df_clean, target_skills)
    multi_factor_ranking = scoring_system.rank_tutors_multi_factor(df_clean, target_skills, target_years, custom_weights)
    
    # Show results
    print(f"\n🏆 TOP 10 TUTORS (Skills-Only Ranking):")
    print(f"{'Rank':<4} {'Name':<20} {'Skills':<6} {'Years':<5} {'Rating':<6} {'City':<12}")
    print("-" * 60)
    for i, tutor in enumerate(skills_only_ranking[:10]):
        print(f"{i+1:<4} {tutor['name']:<20} {tutor['skills_score']:<6.3f} "
              f"{tutor['years_num']:<5.0f} {tutor['rating_norm']:<6.2f} {tutor['city']:<12}")
    
    print(f"\n🏆 TOP 10 TUTORS (Multi-Factor Ranking):")
    print(f"{'Rank':<4} {'Name':<20} {'Score':<6} {'Skills':<6} {'Exp':<5} {'Rating':<6} {'Years':<5}")
    print("-" * 65)
    for i, tutor in enumerate(multi_factor_ranking[:10]):
        print(f"{i+1:<4} {tutor['name']:<20} {tutor['composite_score']:<6.3f} "
              f"{tutor['skills_score']:<6.2f} {tutor['exp_score']:<5.2f} "
              f"{tutor['rating_score']:<6.2f} {tutor['years_num']:<5.0f}")
    
    # Show detailed scores for top 3
    print(f"\n🔍 DETAILED SCORES FOR TOP 3 TUTORS:")
    for i, tutor in enumerate(multi_factor_ranking[:3]):
        print(f"\n{i+1}. {tutor['name']} (ID: {tutor['tutor_id']})")
        print(f"   Composite Score: {tutor['composite_score']:.3f}")
        print(f"   Breakdown:")
        print(f"     - Skills Match: {tutor['skills_score']:.3f} (weight: {custom_weights['skills']:.2f})")
        print(f"     - Experience:   {tutor['exp_score']:.3f} (weight: {custom_weights['experience']:.2f})")
        print(f"     - Rating:       {tutor['rating_score']:.3f} (weight: {custom_weights['rating']:.2f})")
        print(f"   Details: {tutor['years_num']:.0f} years exp, {tutor['rating_norm']:.2f} rating")
    
    # Analysis
    print(f"\n📈 ANALYSIS:")
    skills_top_3_ids = {t['tutor_id'] for t in skills_only_ranking[:3]}
    multi_top_3_ids = {t['tutor_id'] for t in multi_factor_ranking[:3]}
    overlap = len(skills_top_3_ids & multi_top_3_ids)
    
    print(f"   - Top 3 overlap: {overlap}/3 tutors")
    print(f"   - Multi-factor ranking considers quality and experience")
    print(f"   - Custom weights allow personalized preferences")
    
    # Ask if user wants to try different weights
    print(f"\n🔄 Want to try different weights? (y/n): ", end="")
    if input().lower().startswith('y'):
        interactive_demo()


def quick_demo():
    """Quick demonstration with predefined scenarios"""
    
    print("🚀 QUICK DEMO - Predefined Scenarios")
    print("=" * 40)
    
    # Load data
    try:
        df = pd.read_csv('data.csv')
        df_clean = clean_data(df)
    except FileNotFoundError:
        print("❌ Error: data.csv not found")
        return
    
    scoring_system = TutorScoringSystem()
    
    scenarios = [
        {
            'name': 'Math Student (Beginner)',
            'skills': {'Math'},
            'years': 2,
            'weights': {'skills': 0.6, 'experience': 0.2, 'rating': 0.2}
        },
        {
            'name': 'Science Student (Advanced)',
            'skills': {'Physics', 'Chemistry'},
            'years': 8,
            'weights': {'skills': 0.4, 'experience': 0.4, 'rating': 0.2}
        },
        {
            'name': 'Quality-Focused Parent',
            'skills': {'Math', 'Physics'},
            'years': 5,
            'weights': {'skills': 0.3, 'experience': 0.2, 'rating': 0.5}
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print(f"   Target: {scenario['skills']}, {scenario['years']} years")
        print(f"   Weights: S:{scenario['weights']['skills']:.1f} E:{scenario['weights']['experience']:.1f} R:{scenario['weights']['rating']:.1f}")
        
        ranking = scoring_system.rank_tutors_multi_factor(
            df_clean, scenario['skills'], scenario['years'], scenario['weights']
        )
        
        print(f"   Top 3 tutors:")
        for i, tutor in enumerate(ranking[:3]):
            print(f"     {i+1}. {tutor['name']} (Score: {tutor['composite_score']:.3f})")


if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Interactive Demo (custom preferences)")
    print("2. Quick Demo (predefined scenarios)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        interactive_demo()
    elif choice == "2":
        quick_demo()
    else:
        print("Running interactive demo by default...")
        interactive_demo()

