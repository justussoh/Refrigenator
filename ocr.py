from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"

def convert_image(image):
    img = Image.open(image)
    text = pytesseract.image_to_string(img)

    #Separate by line break, and spaces
    splitted = text.split(sep = "\n")

    receipt = []
    for phrase in splitted:
        res = phrase.split(sep = " ")
        for word in res:
            try:
                receipt.append(word.upper())
            except:
                receipt.append(word)

    #Remove duplicate from receipt
    receipt = list(set(receipt))

    return receipt

#Ask for some image
#Function will convert image to lst via -- convert_image("C:\Users\Justin\Desktop\ntuc.jpg")
#Run function add_bulk on the lst

#Loop throug list, ask for number
