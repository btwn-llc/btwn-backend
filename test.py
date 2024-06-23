import requests
import json
from llm import query_openai
from scrape import scrape_youtube_comments

## TEST 4 ##
# complaints = ['**Integrate Makeup Tutorials and Better Products** - Users want repeated and improved makeup tutorials with better products and techniques.', '**Affordable Quality Clothing** - Users appreciate affordable brands but desire better quality in fast fashion apparel like Shein offers.', '**Reliable Shipping and Customer Service** - Dissatisfaction with long shipping times and customer service issues.', '**Inclusive and Comfortable Clothing** - Desire for size inclusivity and age-appropriate, comfortable designs.', '**Ethical Manufacturing** - Concern about unethical labor practices, particularly child labor in fast fashion.', '**Tech with Ethical AI Integration** - Concerns about data privacy and security in AI products from tech giants like Apple.', '**Transparent Pricing and Sales Information** - Users want clear pricing and availability details, especially for online purchases.', '**Cultural and Seasonal Adaptation in Products** - Desire for product availability that matches cultural preferences and seasonal demands.', '**Quality Control on Low-cost Products** - Complaints about low durability and quality of affordable products from brands like Shein.', '**Memorable Customer Experience and Fast Food Customization** - Complaints about product consistency and desire for customizable fast food options similar to other favorite options.'], 
# user_notes = "I am looking to break into the lipstick market specifically."
# url = 'http://127.0.0.1:5000/top-ideas'
# headers = {'Content-Type': 'application/json'}
# payload = {
#     'complaints': complaints,
#     'user_notes': user_notes
# }

# response = requests.post(url, headers=headers, data=json.dumps(payload))
# print("MY RESULT", response.json())

## TEST 3 ##
url = 'http://127.0.0.1:5000/top-complaints'
headers = {'Content-Type': 'application/json'}
payload = {
    'industries': ['fashion'],
    'companies': ['shein']
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print("MY complaints", response.json())
## TEST 2 ##

# url = 'http://127.0.0.1:5000/top-companies'
# headers = {'Content-Type': 'application/json'}
# payload = {
#     'industries': ['tech']
# }

# response = requests.post(url, headers=headers, data=json.dumps(payload))
# print("MY RESULT COMPANIES", response.json())


## TEST 1 ##

# Filter with OpenAI
# results = {
#   "hits": [
#     {
#       "description": "Detailed info and reviews on 66 top Fashion Tech companies and startups in United States in 2024. Get the latest updates on their products, jobs, funding, investors, founders and more.", 
#       "snippets": [
#         "Our transformative process repurposes these valuable materials into raw materials for the consumer goods, fashion and luxury small leather goods industries . We grant SMEs exclusive access, fostering a sustainable future where every leather piece finds purpose, enhancing our world's beauty.", 
#         "We're tracking AI.Fashion, Peralta Clothing and more Fashion Tech companies in United States from the F6S community. Fashion Tech forms part of the Fashion industry, which is the 21st most popular industry and market group. If you're interested in the Fashion market, also check out the top Apparel, Cosmetics, Furniture, Fashion Design or Jewelry companies.", 
#         "Custom, high-quality, sustainable fashion brand/platform offering made-to-order pieces designed by a former Givenchy designer. Solving lack of availability & industry waste by providing unique, sustainable clothing made to specific requirements.", 
#         "We\u2019re alternew, and we\u2019re taking on the fashion industry\u2019s sustainability challenge by building SaaS technology for alterations and repair specialists that modernizes how we extend the life of our clothes."
#       ], 
#       "title": "66 top Fashion Tech companies and startups in United States in 2024 | F6S companies - United States | F6S", 
#       "url": "https://www.f6s.com/companies/fashion-tech/united-states/co"
#     }, 
#     {
#       "description": "Check out this list of the top Fashion companies. See company benefits, info, interviews and more at Built In.", 
#       "snippets": [
#         "In 2005, we launched Brilliant Earth to raise the standards in the jewelry industry while creating beautiful fine jewelry that is different in every way \u2013 how it\u2019s made, how it\u2019s sold, how it\u2019s sourced and crafted, and how it gives back. As a result, we go beyond current industry practices for sourcing, use recycled precious metals to minimize our environmental footprint, and support environmental and social causes through our giving back initiatives.", 
#         "As a result, we go beyond current industry practices for sourcing, use recycled precious metals to minimize our environmental footprint, and support environmental and social causes through our giving back initiatives. Or Mission is to cultivate a more transparent, sustainable, compassionate, and inclusive jewelry industry.", 
#         "Or Mission is to cultivate a more transparent, sustainable, compassionate, and inclusive jewelry industry. Our Mission and ESG Goals are underpinned by our foundational pillars: We believe that demonstrating transparency, through ethical business practices and governance, and enforcing rigorous protocols for sourcing environmentally and socially responsible materials are key to driving change in our industry.", 
#         "We seek ways to create lasting impact, not just in our own value chain and customer communities but also across artisanal small scale mining communities where gemstones and precious metals are sourced. We are committed to creating a representative jewelry industry through our unique products and inclusive experiences for customers, and through a company culture that emphasizes equitable recruiting practices and invests in our diverse employee base."
#       ], 
#       "title": "Top Fashion Companies 2024 | Built In", 
#       "url": "https://builtin.com/companies/type/fashion-companies"
#     }, 
#     {
#       "description": "Today\u2019s retail word is driven by customer experience instead of discounts. Learn more about useful fashion tech companies that elevate customer retention.", 
#       "snippets": [
#         "There is a new trend emerging in the retail world that\u2019s shaking the industry to its core: customers want superior experiences and not just discounts. Many companies struggle to build their strategies around this sentiment \u2013 ASOS recently scrapped A-List instead of rebranding it \u2013 condemning themselves to paddling even though a perfectly fine engine is within a hand\u2019s reach.", 
#         "All of Syte\u2019s products are powered by their proprietary deep learning algorithm based on over 15 years of research, which has been proven in industry evaluations to be 90% accurate in image-to-image search.", 
#         "Being a Software-as-a-Service platform, Poq allows retailers to create highly effective and fully customised native apps in record time. These apps help companies to build stronger brands, sell more products, deepen customer loyalty and deliver highly relevant content, communications and, of course, rewards.", 
#         "On top of that, the technology provides real-time market intelligence on a product\u2019s true-life cycle and behavioral pattern long after it leaves the store. These learnings enable personalized marketing and advertising based on how, where, and when the product is actually being used."
#       ], 
#       "title": "Fashion Tech Companies: How They Improve Customer Experience?", 
#       "url": "https://antavo.com/blog/fashion-tech-companies/"
#     }, 
#     {
#       "description": "Food technology refers to the branch of food science concerned with production, preservation, quality control, and R&D to develop advanced and novel food products | Growth of advanced technologies within the food industry is driving global food tech market growth.", 
#       "snippets": [
#         "Emergence of plant-based meat alternatives, such as products provided by Impossible Foods and Beyond Meat, have revolutionized the food tech industry over the recent past. Growing demand for these food products have led to a rapid establishment of numerous companies producing plant-based food products.", 
#         "Technology has plye a pivotal role in helping food industry adapt to the changing times and cater to growing demand for healthier and sustainable food options. Food lovers and demanding consumers are increasingly spending on food tech innovations owing to its convenience and ability to retain high-quality of food. Consumers today are keen on knowing and understanding the ingredients used in the food, traceability of these ingredients, and have become increasingly aware of food fraud and hygiene factors.", 
#         "Food tech is the portmanteau of the words food and technology and comprises companies and initiatives that leverage advanced technologies such as the Internet of Things (IoT), big data, and Artificial Intelligence (AI) to transform and modernize agriculture and food industry to enhance its sustainability and efficiency \u2013 from preparation of food products to its commercialization and consumption. Food technology enables more efficient food production and maintenance through the introduction of food irradiation and aseptic packaging that eliminate contaminating microbes and improve shelf-life of the products. These technologies are also providing increased protection to crops and maximizing outputs that can help in achieving sustainability goals such as lowering greenhouse gasses, minimizing water waste, and accelerate sequestration of carbon back into the soil.", 
#         "The advent of innovative technologies has changed the world and rules of the game across various end-use industries. Over the last couple of years, food industry has come to terms with the benefits of advanced technologies and has been working towards integrating technologies such as big data or the Internet of Things (IoT) to its business workflow."
#       ], 
#       "title": "Food Technology Market Top Companies Profile 2020-2028 | Food Tech Industry Growth", 
#       "url": "https://www.emergenresearch.com/blog/top-10-companies-redefining-the-future-of-food-technology-industry"
#     }, 
#     {
#       "description": "Discover the Top 8 Fashion Technology Trends plus 16 Top Startups in the field to learn how they impact your business in 2023.", 
#       "snippets": [
#         "The result of this research is data-driven innovation intelligence that improves strategic decision-making by giving you an overview of emerging technologies & startups in the fashion tech industry. These insights are derived by working with our Big Data & Artificial Intelligence-powered StartUs Insights Discovery Platform, covering 2 500 000+ startups & scaleups globally. As the world\u2019s largest resource for data on emerging companies, the SaaS platform enables you to identify relevant startups, emerging technologies & future industry trends quickly & exhaustively.", 
#         "Technology is bringing the fashion industry from physical to digital space. Virtual fashion solutions overcome physical constraints through AR or VR and provide unlimited creative space. These technologies allow customers to try clothing or make-up virtually before buying them.", 
#         "These fashion tech startups are hand-picked based on criteria such as founding year, location, funding raised, and more. Depending on your specific needs, your top picks might look entirely different. ... Book your platform demo! Technology is bringing the fashion industry from physical to digital space.", 
#         "All Reports [PDF] AgriTech Automotive BioTech Circular Economy Construction Energy Engineering FinTech Food \u00b7 Healthcare Industry 4.0 InsurTech Logistics Manufacturing Materials Media Mobility Oil & Gas Packaging \u00b7 Pharma Rail Renewables Retail Smart City SpaceTech Telecom Travel Utillity ... Are you curious about which fashion technology trends & startups will soon impact your business?"
#       ], 
#       "title": "Top 8 Fashion Technology Trends in 2023 | StartUs Insights", 
#       "url": "https://www.startus-insights.com/innovators-guide/fashion-technology-trends/"
#     }, 
#     {
#       "description": "In the wake of the pandemic, fashion technology is playing a starring role in reshaping the sector.", 
#       "snippets": [
#         "Is it fair to say that that until recently the fashion industry has not used these technology tools as much as other industries? Is it in some ways playing catch-up, compared to other sectors? Anita Balchandani: On the one hand, when you look at online adoption in this industry, while it\u2019s nowhere at the order of magnitude of what you see in consumer electronics or music, it\u2019s definitely well ahead of categories such as food and beauty.", 
#         "Having said that, you have a number of key players in the industry that now are partnering with many of these companies, looking to bring these sorts of products to life. Given that kind of collaboration, we are starting to see early markers of this being able to scale and succeed over the next five to ten years. Daniel Eisenberg: Going hand-in-hand with sustainability are issues like social justice, working conditions, and the supply chain: How much are those issues driving the conversation in the industry and forcing it to think about new approaches to doing business?", 
#         "Daniel Eisenberg: You were talking earlier about the use of analytics for inventory management and predictive modeling. Is it fair to say that that until recently the fashion industry has not used these technology tools as much as other industries? Is it in some ways playing catch-up, compared to other sectors?", 
#         "Daniel Eisenberg: You\u2019ve talked previously about the trend of \u201ccasualization\u201d of what people are wearing, and buying often these days, especially with so many people staying home to work during the pandemic. I\u2019m wondering to what extent you think that trend will be permanent. And does a shift like that have long-term implications for the industry, such as needing to rely on technology even more to cater to changing tastes?"
#       ], 
#       "title": "What tech innovation means for the business of fashion", 
#       "url": "https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/what-tech-innovation-means-for-the-business-of-fashion"
#     }, 
#     {
#       "description": "We\u2019ve researched and compiled information on 40 fashion startups primed to profit off of the expected rise in digital channels and other up-and-coming shifts in the fashion world.", 
#       "snippets": [
#         "We\u2019ve researched and compiled information on 40 fashion startups primed to profit off of the expected rise in digital channels and other up-and-coming shifts in the fashion world. Read on for funding information and more on these notable companies.", 
#         "What they do: 4th and Reckless is a UK-based fashion startup that offers affordable and trendy clothing, shoes, and accessories for women. The brand is known for its bold and fashion-forward designs, which are influenced by the latest trends in the fashion industry. 4th and Reckless has a strong presence on social media and has gained a loyal following among fashion-conscious young women.", 
#         "What they do: Bolt Threads creates innovative materials with a focus on preserving the environment and reducing the impact of the textile industry. Materials they\u2019ve produced include Mylo, a leather alternative made out of mycelium, and b-silk protein, a bioengineered substance used in skin and hair care products.", 
#         "The fashion industry is poised for strong growth despite pressure on household incomes and other global conflicts."
#       ], 
#       "title": "40 Trending Fashion Companies & Startups (2024)", 
#       "url": "https://explodingtopics.com/blog/fashion-startups"
#     }, 
#     {
#       "description": "Read article about New fashion startups are launched every day, all over the world. Launched by tech pioneers, most compelling ideas are supported by accelerators such as \u2018Fashion for Good\u2019, Reshape, and LVMH Innovation. and more articles about Textile industary at Fibre2Fashion", 
#       "snippets": [
#         "Some of these fashion startups innovate in VR fashion, Augmented Reality clothing, AI, material design, and styling. Others create new business models in retail, circular supply chains, innovative advertising, and even recruitment. Without further ado, here are the top 15 fashion startups of 2020-2021: ... Holition is a fashion startup company embracing technology to help retailers and brands adopt and use 3D technology and augmented reality.", 
#         "Fibre2fashion.com does not endorse or recommend any article on this site or any product, service or information found within said articles. The views and opinions of the authors who have submitted articles to Fibre2fashion.com belong to them alone and do not reflect the views of Fibre2fashion.com.", 
#         "The Fabricant is a digital fashion house leading the fashion industry towards a new sector of digital-only clothing \u2013 wasting nothing but data and exploiting nothing but imagination.", 
#         "Launched by tech pioneers, most compelling ideas are supported by accelerators such as \u2018Fashion for Good\u2019, Reshape, and LVMH Innovation. Then, when these technologies and business models start to show results, corporate partners kick in, such as the Kering Group, Adidas, Target, or Zalando."
#       ], 
#       "title": "15 Best Sustainable And Tech Fashion Startups - Fibre2Fashion", 
#       "url": "https://www.fibre2fashion.com/industry-article/9055/15-best-sustainable-and-tech-fashion-startups"
#     }, 
#     {
#       "description": "Using our proprietary Seedtable Score, we compiled a list of the fastest-growing technology startups and scaleups in Fashion.", 
#       "snippets": [
#         "Legal Tech... (352) Consumer Social... (294) Cybersecurity... (285) Video... (282) Supply Chain & ...... (275) Pharma... (272) Robotics... (272) Creative Tools... (256) Productivity Tools... (254) Enterprise Soft...... (248) Insuretech... (230) CRM... (214) Future of Work... (210) AR / VR... (210) Internet of Things... (205) Music and Audio... (201) Fitness... (189) Cloud... (182) Service Industry... (162) Food Delivery...", 
#         "Service Industry... (162) Food Delivery... (135) Investing... (133) Space Tech... (130)", 
#         "Skincare and cosmetics products company delivering simple, effective solutions for personal care. ... White label \"scan and go\" technology for retail. ... Platform offering customizable design through industrial manufacturing.", 
#         "White label \"scan and go\" technology for retail. ... Platform offering customizable design through industrial manufacturing. ... Marketplace for premium sneakers. ... Omnichannel eyewear company."
#       ], 
#       "title": "69 Best Fashion Startups to Watch in 2024", 
#       "url": "https://www.seedtable.com/startups-fashion"
#     }, 
#     {
#       "description": "McKinsey\u2019s State of Fashion report offers the best of our research and insights into the fashion industry. Explore the findings from our latest 2024 report.", 
#       "snippets": [
#         "Fashion companies will face economic headwinds, technology shifts, and an evolving competitive landscape in 2024. However, shifting consumer priorities will continue to offer opportunities. ... Storm clouds are gathering, but the experience of recent years shows how the fashion industry may ride out the challenges ahead.", 
#         "These are just some of the findings from The State of Fashion 2024, published by the Business of Fashion (BoF) and McKinsey. The eighth report in the annual series discusses the major themes shaping the fashion economy and assesses the industry\u2019s potential responses.", 
#         "At the same time, lifestyle brands will likely embed technical elements into collections, blurring the lines between functionality and style. ... Generative AI\u2019s creative crossroads. After generative AI\u2019s (gen AI) breakout year in 2023, more use cases are emerging across the industry.", 
#         "According to McKinsey\u2019s analysis of fashion forecasts, the global industry will post top-line growth of 2 to 4 percent in 2024 (exhibit), with regional and country-level variations. Once again, the luxury segment is expected to generate the biggest share of economic profit. However, even there, companies will be challenged by the tough economic environment."
#       ], 
#       "title": "The State of Fashion 2024: Finding pockets of growth as uncertainty reigns", 
#       "url": "https://www.mckinsey.com/industries/retail/our-insights/state-of-fashion"
#     }
#   ], 
#   "latency": 0.23251891136169434
# }
# # Scrape top 5 links
# top_companies_result = []
# for result in results["hits"]:
#     link = result["url"]
#     article_result = scrape_article_content(link)
#     if article_result:
#         top_companies_result.append(article_result)
#         print("Successfully retrieved: ", link)
#     if len(top_companies_result) >= 5:
#         break

# # Filter with OpenAI
# prompt = f"Can you glean the top companies from these results along with a description of them and format it into a list of dictionaries with keys of company_name and company description: {top_companies_result}"
# print("prompt", prompt)
# result = query_openai(prompt)
# print("dana", result)