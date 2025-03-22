import os
# os.chdir(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
# print(os.path.abspath(os.path.join(__file__, '../../..')))

from plugins.VVQuest.services.image_search import ImageSearch

im = ImageSearch('local')

if not os.path.exists(im._get_cache_file()):
    im.generate_cache()

import time
start = time.time()

l = os.listdir('plugins/VVQuest/data/images')
for i in l:
    print(im.search(os.path.basename(i)))
print(time.time() - start)