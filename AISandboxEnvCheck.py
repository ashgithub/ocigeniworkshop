# This scipt does a basic version check for AI Sanbox development env, If yuo have questions please ask in #igiu-ai-learning
import oci
import oracledb
import sys 

print ("AI Sandbox Environment check")
print(f"python version (tested with 3.13.4): {sys.version}")
print(f"oci sdk version (>= 2.161.1): {oci.version.__version__}")
print(f"oraceldb client sdk version( >= 3.4.0): {oracledb.version}")

