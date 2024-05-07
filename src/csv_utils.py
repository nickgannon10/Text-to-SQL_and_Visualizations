def get_csv_string(df):
    from io import StringIO
    import pandas as pd 

    output = StringIO()
    df.to_csv(output)
    csv_string = output.getvalue()

    return csv_string, df

def encode_seaborn_plot_to_base64(plot_variable):
    import io
    import base64
    # Create a BytesIO object to temporarily store the plot
    buffer = io.BytesIO()
    
    # Save the plot to the BytesIO buffer
    plot_variable.figure.savefig(buffer, format='png')
    
    # Get the bytes data from the buffer
    image_bytes = buffer.getvalue()
    
    # Encode the image bytes in base64
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    
    return encoded_image