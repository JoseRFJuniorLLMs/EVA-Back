import sys
sys.path.insert(0, 'd:\\dev\\EVA-back\\eva-enterprise')

from main import app

print(f"Total routes: {len(app.routes)}")
print("\nRoutes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"  {list(route.methods)} {route.path}")
