from datetime import datetime

def text_array_to_file(text_array):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = "OCRScan_" + f"{timestamp}.txt"

    with open(output_file, "w") as output:
        output.write("OCR Scan results \n \n \n")
        for frame_text, frame_i in text_array:
            output.write(f"Frame: {frame_i}")
            output.write("\n----------------------------------\n")
            output.write(f"{frame_text}")
            output.write("----------------------------------")
            output.write("\n")        
    
    return output_file