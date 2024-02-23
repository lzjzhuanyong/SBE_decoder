def decoder(data):

    blockLength = data[0:2]
    templateId = data[2:4]
    schemaId = data[4:6]
    version = data[6:8]
    timestamp = data[8:16]

    return {
        "blockLength": int.from_bytes(blockLength,byteorder='little'),
        "templateId": int.from_bytes(templateId,byteorder='little'),
        "schemaId": int.from_bytes(schemaId,byteorder='little'),
        "version": int.from_bytes(version,byteorder='little'),
        "timestamp": int.from_bytes(timestamp,byteorder='little')
    }

