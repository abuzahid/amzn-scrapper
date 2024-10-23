
def get_title(soup):

    try:
        # Outer Tag Object
        title = soup.find("span", attrs={"id":'productTitle'})
        
        # Inner NavigatableString Object
        title_value = title.text

        # Title as a string value
        title_string = title_value.strip()

    except AttributeError:
        title_string = ""

    return title_string


def get_price(soup):

    try:
        # price = soup.find("span", attrs={'id':'a-price aok-align-center reinventPricePriceToPayMargin priceToPay'}).string.strip()
        dec = soup.find("span", attrs={'class':'a-price-whole'}).text.strip()
        frac = soup.find("span", attrs={'class':'a-price-fraction'}).string.strip()
        price = '$'+dec + frac

    except AttributeError:

        try:
            # If there is some deal price
            price = soup.find("span", attrs={'id':'a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage'}).string.strip()

        except:
            price = ""

    return price


def get_specification_data(soup):
    try:
        # Find the table
        table = soup.find('table', {'id': 'technicalSpecifications_section_1'})
        
        # Initialize variables
        brand = ""
        model = ""
        
        # Get all rows from the table
        rows = table.find_all('tr')
        
        # Iterate through rows
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:
                header = cols[0].text.strip()
                value = cols[1].text.strip()
                
                # Get brand and model
                if header == "Brand, Seller, or Collection Name":
                    brand = value
                elif header == "Model number":
                    model = value
                
                # If we have both values, we can exit the loop
                if brand and model:
                    break
        
        return brand, model

    except AttributeError:
        return "", ""
    

def get_rating(soup):

    try:
        rating = soup.find("i", attrs={'class':'a-icon a-icon-star a-star-4-5'}).string.strip()
    
    except AttributeError:
        try:
            rating = soup.find("span", attrs={'class':'a-icon-alt'}).string.strip()
        except:
            rating = ""	

    if rating:
        rating=rating.split(" ")[0]

    return rating

def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id':'acrCustomerReviewText'}).string.strip()

    except AttributeError:
        review_count = ""	

    return review_count

def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id':'availability'})
        available = available.find("span").string.strip()

    except AttributeError:
        available = "Not Available"	

    return available