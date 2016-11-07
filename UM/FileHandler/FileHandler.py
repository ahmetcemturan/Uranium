# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginRegistry import PluginRegistry
from UM.Logger import Logger

##  Central class for reading and writing meshes.
#   This class is created by Application and handles reading and writing mesh files.
class FileHandler:
    def __init__(self, writer_type, reader_type):
        super().__init__()

        self._readers = {}
        self._writers = {}

        self._writer_type = writer_type
        self._reader_type = reader_type

        PluginRegistry.addType(self._writer_type, self.addWriter)
        PluginRegistry.addType(self._reader_type, self.addReader)

    ##  Get a writer object that supports writing the specified mime type
    #
    #   \param mime The mime type that should be supported.
    #   \return A |type{Writer} instance or None if no writer supports the specified mime type. If there are multiple
    #           writers that support the specified mime type, the first entry is returned.
    def getWriterByMimeType(self, mime):
        writer_data = PluginRegistry.getInstance().getAllMetaData(filter={self._writer_type: {}}, active_only=True)
        for entry in writer_data:
            for output in entry["mesh_writer"].get("output", []):
                if mime == output["mime_type"]:
                    return self._mesh_writers[entry["id"]]
        return None

    ##  Get list of all supported filetypes for writing.
    #   \return List of dicts containing id, extension, description and mime_type for all supported file types.
    def getSupportedFileTypesWrite(self):
        supported_types = []
        meta_data = PluginRegistry.getInstance().getAllMetaData(filter={self._writer_type: {}}, active_only=True)
        for entry in meta_data:
            for output in entry[self._writer_type].get("output", []):
                ext = output.get("extension", "")
                description = output.get("description", ext)
                mime_type = output.get("mime_type", "text/plain")
                supported_types.append({
                    "id": entry["id"],
                    "extension": ext,
                    "description": description,
                    "mime_type": mime_type
                })
        return supported_types

    # Get list of all supported file types for reading.
    # \returns List of strings with all supported file types.
    def getSupportedFileTypesRead(self):
        supported_types = {}
        meta_data = PluginRegistry.getInstance().getAllMetaData(filter={self._reader_type: {}}, active_only=True)
        for entry in meta_data:
            if self._reader_type in entry:
                for input_type in entry[self._reader_type]:
                    ext = input_type.get("extension", None)
                    if ext:
                        description = input_type.get("description", ext)
                        supported_types[ext] = description
        return supported_types

    def addReader(self, reader):
        self._readers[reader.getPluginId()] = reader

    def addWriter(self, writer):
        self._writers[writer.getPluginId()] = writer

    # Try to read the data from a file using a specified Reader.
    # \param reader Reader to read the file with.
    # \param file_name The name of the file to load.
    # \param kwargs Keyword arguments.
    # \returns None if nothing was found
    def readerRead(self, reader, file_name, **kwargs):
        raise NotImplementedError("readerRead must be implemented by subclasses.")

    ##  Get a mesh writer object that supports writing the specified mime type
    #
    #   \param mime The mime type that should be supported.
    #   \return A MeshWriter instance or None if no mesh writer supports the specified mime type. If there are multiple
    #           writers that support the specified mime type, the first entry is returned.
    def getWriterByMimeType(self, mime):
        writer_data = PluginRegistry.getInstance().getAllMetaData(filter={self._writer_type: {}}, active_only=True)
        for entry in writer_data:
            for output in entry[self._writer_type].get("output", []):
                if mime == output["mime_type"]:
                    return self._writers[entry["id"]]

        return None

    ##  Get an instance of a mesh writer by ID
    def getWriter(self, writer_id):
        if writer_id not in self._writers:
            return None

        return self._writers[writer_id]

    ##  Find a Reader that accepts the given file name.
    #   \param file_name The name of file to load.
    #   \returns Reader that accepts the given file name. If no acceptable Reader is found None is returned.
    def getReaderForFile(self, file_name):
        for id, reader in self._readers.items():
            try:
                if reader.acceptsFile(file_name):
                    return reader
            except Exception as e:
                Logger.log("e", str(e))

        return None