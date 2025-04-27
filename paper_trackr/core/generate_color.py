import hashlib

# generate a hash for keyword and transform to hexcolor (only 6 first chars of the hex)
# ngl, im pretty happy with that way to generate persistent colors!
def keyword_to_color(keyword):
    hash_object = hashlib.md5(keyword.encode())     # generate an md5 hash 
    hex_digest = hash_object.hexdigest()            # convert hash to hex 
    color = f"#{hex_digest[:6]}"                    # keep the first 6 chars of the hex
    return color 


# generate pastel colors to background
def keyword_to_pastel_color(keyword):
    hash_object = hashlib.md5(keyword.encode())
    hash_digest = hash_object.hexdigest()
    
    # use part of the hash to create RGB values
    r = int(hash_digest[0:2], 16)
    g = int(hash_digest[2:4], 16)
    b = int(hash_digest[4:6], 16)

    # adjust the color to make it lighter, giving it a pastel appearance
    r = int((r + 255) / 2)
    g = int((g + 255) / 2)
    b = int((b + 255) / 2)

    # return the color in hexadecimal format 
    return f'#{r:02x}{g:02x}{b:02x}'


# generate text colors (if the background is light, return black text, otherwise white)
def get_contrast_text_color(bg_hex_color):
    # convert hex color to RGB values 
    bg_hex_color = bg_hex_color.lstrip('#')
    r = int(bg_hex_color[0:2], 16)
    g = int(bg_hex_color[2:4], 16)
    b = int(bg_hex_color[4:6], 16)

    # calculate perceptual luminance of the background color 
    luminance = (0.299 * r + 0.587 * g + 0.114 * b)

    # return black text if background is light 
    # return white text if background is dark
    return '#000000' if luminance > 186 else '#ffffff'
