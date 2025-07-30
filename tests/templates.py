import os
for root, dirs, files in os.walk('templates'):
    for file in files:
        print(os.path.join(root, file))
