import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    exit(1)

# Initialize Supabase client with service role key to bypass RLS
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def seed_data():
    print("--- Starting database seeding ---")

    # Sample users to create
    sample_users = [
        {
            "email": "sarah.investor@example.com",
            "password": "password123",
            "full_name": "Sarah Investor",
            "literacy": "intermediate",
            "risk_data": {
                "age_range": "30-40",
                "income_range": "$80k-$120k",
                "self_reported_tolerance": "Medium",
                "investment_horizon_years": 15,
                "primary_goal": "Retirement",
                "has_dependents": True,
                "savings_level": "Moderate",
                "debt_level": "Low",
                "predicted_risk_profile": "Moderate",
                "confidence_score": 0.92
            }
        },
        {
            "email": "mike.aggressive@example.com",
            "password": "password123",
            "full_name": "Mike Aggressive",
            "literacy": "expert",
            "risk_data": {
                "age_range": "20-30",
                "income_range": "$150k+",
                "self_reported_tolerance": "High",
                "investment_horizon_years": 30,
                "primary_goal": "Wealth Accumulation",
                "has_dependents": False,
                "savings_level": "High",
                "debt_level": "None",
                "predicted_risk_profile": "Aggressive",
                "confidence_score": 0.95
            }
        },
        {
            "email": "jane.conservative@example.com",
            "password": "password123",
            "full_name": "Jane Conservative",
            "literacy": "beginner",
            "risk_data": {
                "age_range": "50-60",
                "income_range": "$50k-$80k",
                "self_reported_tolerance": "Low",
                "investment_horizon_years": 5,
                "primary_goal": "Capital Preservation",
                "has_dependents": False,
                "savings_level": "Moderate",
                "debt_level": "Moderate",
                "predicted_risk_profile": "Conservative",
                "confidence_score": 0.88
            }
        }
    ]

    for user_info in sample_users:
        print(f"Creating user: {user_info['email']}...")
        
        try:
            # 1. Create User in auth.users (this triggers profile creation via SQL trigger)
            # Note: In a real Supabase setup, this uses the admin API
            auth_response = supabase.auth.admin.create_user({
                "email": user_info["email"],
                "password": user_info["password"],
                "user_metadata": {"full_name": user_info["full_name"]},
                "email_confirm": True
            })
            
            user_id = auth_response.user.id
            print(f"User created with ID: {user_id}")

            # 2. Update Profile (literacy level)
            supabase.table("profiles").update({
                "financial_literacy_level": user_info["literacy"]
            }).eq("id", user_id).execute()
            print(f"Profile updated for {user_info['full_name']}")

            # 3. Create Risk Assessment
            risk_data = user_info["risk_data"]
            risk_data["user_id"] = user_id
            # Mock SHAP and top features
            risk_data["shap_values"] = {"age": 0.15, "income": 0.25, "debt": -0.1}
            risk_data["top_features"] = ["income", "age", "investment_horizon"]
            
            assessment_response = supabase.table("risk_assessments").insert(risk_data).execute()
            assessment_id = assessment_response.data[0]["id"]
            print(f"Risk assessment created for {user_info['full_name']}")

            # 4. Create a sample Fund Recommendation
            supabase.table("fund_recommendations").insert({
                "assessment_id": assessment_id,
                "user_id": user_id,
                "fund_name": "Vanguard Total Stock Market Index Fund" if risk_data["predicted_risk_profile"] != "Conservative" else "Vanguard Total Bond Market ETF",
                "fund_type": "Equity" if risk_data["predicted_risk_profile"] != "Conservative" else "Fixed Income",
                "narrative": f"Based on your {risk_data['predicted_risk_profile']} risk profile, this fund provides optimal diversification.",
                "rationale_points": ["Low expense ratio", "Broad market exposure", "Aligned with horizon"],
                "suitability_score": 0.94
            }).execute()
            print(f"Fund recommendation created for {user_info['full_name']}")

        except Exception as e:
            if "already exists" in str(e).lower() or "unique constraint" in str(e).lower():
                print(f"Warning: User {user_info['email']} already exists. Skipping.")
            else:
                print(f"Error seeding user {user_info['email']}: {e}")

    print("\n--- Seeding completed successfully! ---")

if __name__ == "__main__":
    seed_data()
