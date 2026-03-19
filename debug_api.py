import py_clob_client.client as client
import py_clob_client.clob_types as types
import inspect

print("--- CLOBCliient Methods ---")
print([m[0] for m in inspect.getmembers(client.ClobClient, predicate=inspect.isfunction)])

print("\n--- types elements ---")
print(dir(types))
