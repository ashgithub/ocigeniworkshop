"""
What this file does:
Demonstrates Oracle SELECT AI functionality using the Python select-ai library. It runs natural language queries on the WORKSHOP_ADMIN.STUDENTS table to showcase student profile information, providing a Python alternative to SQL-based SELECT AI queries.

Documentation to reference:
- Oracle 23ai Select AI: https://docs.oracle.com/en/cloud/paas/autonomous-database/select-ai/
- Python Select AI Library: https://github.com/oracle/python-select-ai
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci

Relevant slack channels:
- #adb-select-ai-users: questions about Oracle 23ai Select AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).
- Ensure python-select-ai library is installed: pip install oracle-select-ai

How to run the file:
uv run database/selectai_demo.py

Comments to important sections of file:
- Step 1: Load config and initialize database connection.
- Step 2: Set up SELECT AI profile.
- Step 3: Demonstrate Profile methods (narrate, show_sql, explain_sql, run_sql, chat, generate, get_attributes, list).
- Step 4: Additional examples with Profile.run_sql().
- Step 5: Interactive query loop for custom questions.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
from envyaml import EnvYAML
import oracledb
import select_ai

# Load environment variables
load_dotenv()

# Configuration
SANDBOX_CONFIG_FILE = "sandbox.yaml"

def load_config():
    """Load configuration from sandbox.yaml."""
    try:
        return EnvYAML(SANDBOX_CONFIG_FILE)
    except FileNotFoundError:
        print(f"Error: Configuration file '{SANDBOX_CONFIG_FILE}' not found.")
        return None

def main():
    """Main demonstration function."""
    print("Oracle SELECT AI Demonstration - Student Profiles")
    print("=" * 50)

    # Load configuration
    scfg = load_config()
    if not scfg:
        return 1

    db_cfg = scfg["db"]
    wallet_path = os.path.expanduser(db_cfg["walletPath"])

    try:
        # Connect to Oracle using existing database credentials
        print("Connecting to Oracle database...")
        select_ai.connect(
            user="WORKSHOP_ADMIN",
            password=db_cfg["password"],
            dsn=db_cfg["dsn"],
            config_dir=wallet_path,
            wallet_location=wallet_path,
            wallet_password=db_cfg["walletPass"],
        )
        print("Connected successfully!")

        # Create AI profile
        profile_name = 'workshop_app_profile'
        print(f"\nCreating AI profile '{profile_name}'...")
        profile = select_ai.Profile(profile_name=profile_name)
        print("Profile created!")

        # Comprehensive demonstration of Profile methods
        # Adapted from selectai.sql examples for WORKSHOP_ADMIN.STUDENTS table

        print("\n" + "="*60)
        print("DEMONSTRATING PROFILE METHODS")
        print("="*60)

        # 1. Profile.narrate() - Returns natural language answers
        print("\n1. Profile.narrate() - Natural language answers")
        print("-" * 50)
        try:
            result = profile.narrate(prompt="How many students exist?")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

        # 2. Profile.show_sql() - Shows the generated SQL without executing
        print("\n2. Profile.show_sql() - Show generated SQL")
        print("-" * 50)
        try:
            sql = profile.show_sql(prompt="How many students are from Austin?")
            print(f"Generated SQL: {sql}")
        except Exception as e:
            print(f"Error: {e}")

        # 3. Profile.explain_sql() - Explains the generated SQL
        print("\n3. Profile.explain_sql() - Explain SQL execution plan")
        print("-" * 50)
        try:
            explanation = profile.explain_sql(prompt="List students who have completed their team introductions")
            print(f"Explanation: {explanation}")
        except Exception as e:
            print(f"Error: {e}")

        # 4. Profile.run_sql() - Execute SQL and return results (DataFrame)
        print("\n4. Profile.run_sql() - Execute and return results")
        print("-" * 50)
        try:
            df = profile.run_sql(prompt="What are the different teams and how many students are in each?")
            print(f"Columns: {list(df.columns)}")
            print(f"Results ({len(df)} rows):")
            print(df.to_string(index=False))
        except Exception as e:
            print(f"Error: {e}")

        # 5. Profile.chat() - Conversational queries
        print("\n5. Profile.chat() - Conversational interface")
        print("-" * 50)
        try:
            response = profile.chat(prompt="How many students have acknowledged the workshop?")
            print(f"Chat response: {response}")
        except Exception as e:
            print(f"Error: {e}")

        # 6. Profile.generate() - Generate content based on data
        print("\n6. Profile.generate() - Generate content")
        print("-" * 50)
        try:
            generated = profile.generate(prompt="Create a report about student locations")
            print(f"Generated content: {generated}")
        except Exception as e:
            print(f"Error: {e}")

        # 7. Profile.get_attributes() - Get profile configuration
        print("\n7. Profile.get_attributes() - Get profile attributes")
        print("-" * 50)
        try:
            attrs = profile.get_attributes()
            print(f"Profile attributes: {attrs}")
        except Exception as e:
            print(f"Error: {e}")

        # 8. Profile.list() - List available profiles (class method)
        print("\n8. Profile.list() - List available profiles")
        print("-" * 50)
        try:
            profiles = profile.list()
            print(f"Available profiles: {profiles}")
        except Exception as e:
            print(f"Error: {e}")

        # Additional examples with Profile.run_sql()
        print("\n" + "="*60)
        print("ADDITIONAL EXAMPLES WITH Profile.run_sql()")
        print("="*60)

        additional_queries = [
            "Show me all student profiles with their names and locations",
            "List students by location and show their team information",
            "Find students who have not completed introductions",
        ]

        for i, query in enumerate(additional_queries, 10):
            print(f"\n{i}. Profile.run_sql(): {query}")
            print("-" * 50)
            try:
                df = profile.run_sql(prompt=query)
                print(f"Columns: {list(df.columns)}")
                print(f"Results ({len(df)} rows):")
                if len(df) > 0:
                    print(df.head().to_string(index=False))  # Show first 5 rows
                    if len(df) > 5:
                        print(f"... and {len(df) - 5} more rows")
                else:
                    print("No results found")
            except Exception as e:
                print(f"Error executing query: {e}")

        # Interactive query loop
        print("Enter natural language queries about student profiles (or 'quit' to exit):")
        while True:
            try:
                user_query = input("\nQuery> ").strip()
                if user_query.lower() in ['quit', 'exit', 'q']:
                    break
                if user_query:
                    print(f"Executing: {user_query}")
                    print("-" * 40)
                    df = profile.run_sql(prompt=user_query)
                    print(f"Columns: {list(df.columns)}")
                    print(f"Results ({len(df)} rows):")
                    print(df.to_string(index=False))
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Oracle credentials are configured in sandbox.yaml")
        print("And ensure python-select-ai library is installed")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
