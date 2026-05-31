from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["sdiamond"]

products = db["products"]

products.delete_many({})

products_data = [

# RINGS
{"name":"Royal Bloom Ring","type":"ring","material":"gold","stone":["ruby"],"price":18900,"weight":4.2,"image":"Royal Bloom Ring.jpg","description":"Елегантне золоте кільце з рубіном для особливих моментів."},
{"name":"Diamond Grace Ring","type":"ring","material":"platinum","stone":["diamond"],"price":24500,"weight":3.9,"image":"Diamond Grace Ring.jpg","description":"Вишукане платинове кільце з діамантом, символ розкоші."},
{"name":"Sapphire Aura Ring","type":"ring","material":"gold","stone":["sapphire"],"price":19800,"weight":4.1,"image":"Sapphire Aura Ring.jpg","description":"Золоте кільце з сапфіром, що підкреслює стиль."},
{"name":"Amethyst Dream Ring","type":"ring","material":"silver","stone":["amethyst"],"price":8200,"weight":3.5,"image":"Amethyst Dream Ring.jpg","description":"Легке срібне кільце з аметистом для щоденного образу."},
{"name":"Golden Star Ring","type":"ring","material":"gold","stone":["diamond"],"price":21200,"weight":4.3,"image":"Golden Star Ring.jpg","description":"Золоте кільце з діамантом у формі сяйва зірки."},
{"name":"Velvet Ruby Ring","type":"ring","material":"gold","stone":["ruby"],"price":17600,"weight":4.0,"image":"Velvet Ruby Ring.jpg","description":"Глибокий рубін у золоті — класика і елегантність."},
{"name":"Silver Sapphire Ring","type":"ring","material":"silver","stone":["sapphire"],"price":9800,"weight":3.7,"image":"Silver Sapphire Ring.jpg","description":"Срібне кільце з сапфіром у мінімалістичному стилі."},
{"name":"Platinum Diamond Ring","type":"ring","material":"platinum","stone":["diamond"],"price":26800,"weight":4.5,"image":"Platinum Diamond Ring.jpg","description":"Преміум кільце з платини з діамантом."},

# EARRINGS
{"name":"Diamond Light Earrings","type":"earrings","material":"platinum","stone":["diamond"],"price":22100,"weight":3.0,"image":"Diamond Light Earrings.jpg","description":"Сережки з діамантами, що сяють як світло."},
{"name":"Ruby Flame Earrings","type":"earrings","material":"gold","stone":["ruby"],"price":15600,"weight":3.2,"image":"Ruby Flame Earrings.jpg","description":"Яскраві сережки з рубінами в золоті."},
{"name":"Sapphire Sky Earrings","type":"earrings","material":"silver","stone":["sapphire"],"price":9400,"weight":2.9,"image":"Sapphire Sky Earrings.jpg","description":"Сережки кольору неба з сапфіром."},
{"name":"Amethyst Glow Earrings","type":"earrings","material":"silver","stone":["amethyst"],"price":8800,"weight":3.1,"image":"Amethyst Glow Earrings.jpg","description":"Ніжні сережки з аметистом."},
{"name":"Golden Diamond Drop","type":"earrings","material":"gold","stone":["diamond"],"price":20300,"weight":3.4,"image":"Golden Diamond Drop.jpg","description":"Золоті сережки з підвісним діамантом."},
{"name":"Royal Ruby Drops","type":"earrings","material":"gold","stone":["ruby"],"price":16400,"weight":3.0,"image":"Royal Ruby Drops.jpg","description":"Розкішні сережки з рубінами."},
{"name":"Silver Diamond Studs","type":"earrings","material":"silver","stone":["diamond"],"price":11000,"weight":2.6,"image":"Silver Diamond Studs.jpg","description":"Класичні срібні сережки з діамантами."},

# BRACELETS
{"name":"Diamond Line Bracelet","type":"bracelet","material":"platinum","stone":["diamond"],"price":29500,"weight":7.5,"image":"Diamond Line Bracelet.jpg","description":"Браслет з лінією діамантів."},
{"name":"Ruby Charm Bracelet","type":"bracelet","material":"gold","stone":["ruby"],"price":17500,"weight":6.5,"image":"Ruby Charm Bracelet.jpg","description":"Золотий браслет з рубіновими вставками."},
{"name":"Sapphire Ocean Bracelet","type":"bracelet","material":"silver","stone":["sapphire"],"price":12400,"weight":6.2,"image":"Sapphire Ocean Bracelet.jpg","description":"Браслет з сапфірами у морському стилі."},
{"name":"Amethyst Grace Bracelet","type":"bracelet","material":"silver","stone":["amethyst"],"price":9900,"weight":6.0,"image":"Amethyst Grace Bracelet.jpg","description":"Срібний браслет з аметистами."},
{"name":"Golden Spark Bracelet","type":"bracelet","material":"gold","stone":["diamond"],"price":22800,"weight":6.8,"image":"Golden Spark Bracelet.jpg","description":"Блискучий золотий браслет з діамантами."},
{"name":"Ruby Crown Bracelet","type":"bracelet","material":"gold","stone":["ruby"],"price":18400,"weight":6.4,"image":"Ruby Crown Bracelet.jpg","description":"Браслет з рубінами у королівському стилі."},
{"name":"Silver Diamond Chain","type":"bracelet","material":"silver","stone":["diamond"],"price":13500,"weight":6.3,"image":"Silver Diamond Chain.jpg","description":"Срібний браслет-ланцюг з діамантами."},

# PENDANTS
{"name":"Diamond Heart Pendant","type":"pendant","material":"platinum","stone":["diamond"],"price":21000,"weight":2.8,"image":"Diamond Heart Pendant.jpg","description":"Підвіска у формі серця з діамантом."},
{"name":"Ruby Rose Pendant","type":"pendant","material":"gold","stone":["ruby"],"price":15800,"weight":2.9,"image":"Ruby Rose Pendant.jpg","description":"Підвіска-троянда з рубіном."},
{"name":"Sapphire Star Pendant","type":"pendant","material":"silver","stone":["sapphire"],"price":8900,"weight":2.7,"image":"Sapphire Star Pendant.jpg","description":"Підвіска у формі зірки з сапфіром."},
{"name":"Amethyst Moon Pendant","type":"pendant","material":"silver","stone":["amethyst"],"price":7400,"weight":2.9,"image":"Amethyst Moon Pendant.jpg","description":"Місячна підвіска з аметистом."},
{"name":"Golden Diamond Bloom","type":"pendant","material":"gold","stone":["diamond"],"price":19300,"weight":3.0,"image":"Golden Diamond Bloom.jpg","description":"Квіткова підвіска з діамантами."},
{"name":"Ruby Sun Pendant","type":"pendant","material":"gold","stone":["ruby"],"price":16200,"weight":2.8,"image":"Ruby Sun Pendant.jpg","description":"Сонячна підвіска з рубіном."},
{"name":"Silver Sapphire Drop","type":"pendant","material":"silver","stone":["sapphire"],"price":9100,"weight":2.6,"image":"Silver Sapphire Drop.jpg","description":"Срібна підвіска з сапфіром."}

]

products.insert_many(products_data)

print("Товари успішно додані в sdiamond.products")