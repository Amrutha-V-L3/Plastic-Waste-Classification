import cv2
import numpy as np
import tensorflow as tf

# Load the MNIST model
p=r"C:\Users\MSI\Downloads\mnist_digit_model.h5"
mnist_model = tf.keras.models.load_model(p)

# Load the resin number model
p1=r"C:\Users\MSI\Downloads\resin_classifier.h5"
resin_model = tf.keras.models.load_model(p1)

# Map resin numbers to grade names and recycling costs
resin_info = {
    1: ("PET ", 10),  # Example: 10 rupees/kg
    2: ("HDPE ", 15),
    3: ("PVC ", 20),
    4: ("LDPE ", 25),
    5: ("PP ", 30),
    6: ("PS ", 30),
    7: ("Other Resins", 30),
    8: ("No Plastic Detected", 0)
}

# Start video capture
cap = cv2.VideoCapture(0)  # 0 is the default webcam

# Set frame dimensions (optional)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    # Read frames from the camera
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame. Exiting...")
        break

    # Define a small bounding box in the center of the frame
    box_start = (270, 190)
    box_end = (370, 290)
    cropped_frame = frame[190:290, 270:370]  # Crop the region inside the box

    # Preprocess for the MNIST model
    gray_cropped = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    resized_cropped = cv2.resize(gray_cropped, (28, 28))  # Resize for MNIST
    normalized_cropped = resized_cropped / 255.0  # Normalize pixel values
    mnist_input = normalized_cropped.reshape(1, 28, 28, 1)  # Add batch and channel dimensions

    # Predict the digit using the MNIST model
    mnist_predictions = mnist_model.predict(mnist_input)
    detected_number = np.argmax(mnist_predictions)

    # Check if the detected number is valid (1 to 7 or 8 for no plastic)
    if detected_number in resin_info:
        grade_name, recycling_cost = resin_info[detected_number]
    else:
        grade_name, recycling_cost = "Unknown Resin", 0

    # Display the detected number and corresponding resin info
    label = f"Number: {detected_number} - {grade_name} - Cost: Rs.{recycling_cost}"
    cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Draw the bounding box
    cv2.rectangle(frame, box_start, box_end, (255, 0, 0), 2)

    # Display the frame
    cv2.imshow("Resin Code and Plastic Grade Detection", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
