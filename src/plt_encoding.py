import io
import base64

def encode_seaborn_plot_to_base64(plot_variable):
    buffer = io.BytesIO()
    plot_variable.figure.savefig(buffer, format='png')
    image_bytes = buffer.getvalue()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    
    return encoded_image