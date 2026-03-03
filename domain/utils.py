import base64

class Utils:

	@staticmethod
	def bytes_to_str(data) -> str:
		return base64.b64encode(data).decode('utf-8')

	@staticmethod
	def str_to_bytes(btext) -> bytes:
		if btext is None:
			raise ValueError("btext is None")

		# Accept either a Base64 string or Base64 bytes
		if isinstance(btext, str):
			btext = btext.encode('utf-8')
		elif isinstance(btext, (bytes, bytearray)):
			btext = bytes(btext)
		else:
			raise TypeError(f"btext must be str or bytes, got {type(btext).__name__}")

		return base64.b64decode(btext, validate=True)





