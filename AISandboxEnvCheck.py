# This scipt does a basic version check for AI Sanbox development env, If yuo have questions please ask in #igiu-ai-learning
import oci
import oracledb
import sys 

print ("AI Sandbox Environment chec ")
print(f"python version (tested will 3.11.5): {sys.version}")
print(f"oci sdk version (> 2.139.0): {oci.version.__version__}")
print(f"oraceldb client sdk version( > 2.5.0): {oracledb.version}")

