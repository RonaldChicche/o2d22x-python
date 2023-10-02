# These are the error codes with the corresponding error message

error_codes = {
    "0000": "No errors",
    "0100": "No application is currently loaded in the sensor.",
    "0105": "Invalid input parameter",
    "0108": "The sensor is in an operation mode which does not permit the execution of commands.",
    "0110": "Fatal internal error.",
    "0902": "Application to be activated not found.",
    "1000": "It is not possible to trigger the sensor because trigger function via TCP/IP is not active.",
    "1300": "Internal fault during the image transmission from / to the sensor.",
    "1600": "The user tries to obtain a result although no results are available in the sensor.",
    "1601": "The command cannot be executed because the sensor is currently decoding.",
    "1602": "An image is uploaded to the sensor for evaluation. The format detected does not match that of the currently activated application.",
    "1603": "It is not possible to upload an application to the sensor if the external selection of the application is activated.",
    "1604": "The user sends a trigger to the device via TCP/IP. Due to an internal fault the sensor cannot process the trigger."
}

error_solutions = {
    "0000": None,
    "0100": "Some commands require a running application to be loaded. If this is not the case, an error occurs.",
    "0105": "Read the command documentation to send the required information to the sensor.",
    "0108": "Check the command documentation to see when the command can be executed.",
    "0110": "Reboot the sensor.",
    "0902": "Check whether the application number is correct. Check also if the application can be edited using the PC Software.",
    "1000": "Review the sensor configuration to change the sensor trigger mode.",
    "1300": "Check which is the required image format and if all parameters for the results via TCP/IP are correct. In case of a problem during the transmission of information, check whether the information to be sent is correct.",
    "1600": None,
    "1601": "Try to execute the command again.",
    "1602": "Edit the running application to check which is the required image format.",
    "1603": "Use the PC Software to deactivate the external selection of the application.",
    "1604": "This error code shows a sensor failure. Normally the sensor tries to remedy the failure itself. If this error occurs again, reboot the sensor."
}

# This is the serialization format of binary data with header version 3.
serialization_format = {
    0x0000: ["CHUNK_TYPE", "Defines the type of the chunk.", 4],
    0x0004: ["CHUNK_SIZE", "Size of the whole image chunk in bytes.", 4],
    0x0008: ["HEADER_SIZE", "Number of bytes starting from 0x0000 until BINARY_DATA."
                            "The number of bytes must be a multiple of 16, and the minimum value is 0x40 (64).", 4],
    0x000C: ["HEADER_VERSION", "Version number of the header (=3).", 4],
    0x0010: ["IMAGE_WIDTH", "Image width in pixel. Applies only if BINARY_DATA contains an image. "
                            "Otherwise this is set to the length of BINARY_DATA.", 4],
    0x0014: ["IMAGE_HEIGHT", "Image height in pixel. Applies only if BINARY_DATA contains an image. "
                             "Otherwise this is set to 1.", 4],
    0x0018: ["PIXEL_FORMAT", "Pixel format. Applies only to image binary data. For generic binary data "
                             "this is set to FORMAT_8U unless specified otherwise for a particular chunk type.", 4],
    0x001C: ["TIME_STAMP", "Timestamp in uS", 4],
    0x0020: ["FRAME_COUNT", "Continuous frame count.", 4],
    0x0024: ["STATUS_CODE", "This field is used to communicate errors on the device.", 4],
    0x0028: ["TIME_STAMP_SEC", "Timestamp seconds", 4],
    0x002C: ["TIME_STAMP_NSEC", "Timestamp nanoseconds", 4],
    0x0030: ["META_DATA", "UTF-8 encoded null-terminated JSON object. The content of the JSON object is depending "
                          "on the CHUNK_TYPE.", 4]}
bmp_serialization_format = {
    
}