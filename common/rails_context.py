import inspect
import functools


class RailsContext:
	error = ""
	details = ""

	def __init__(self):
		self.error = ""

	def hasError(self):
		if not self.error:
			return False
		else:
			return True


	def setError(self, dv, msg):
		self.error = msg
		return dv


	def setException(self, dv, msg, ex):
		self.error = msg
		self.details = str(ex)
		return dv



def railway(fn):
	sig = inspect.signature(fn)
	params = sig.parameters
	if not 'context' in params: raise TypeError("Missing railway context")

	@functools.wraps(fn)
	def wrapper(self, context: RailsContext, *args, **kwargs):
		if context is None:	raise TypeError("Missing railway context")
		if context.hasError(): return None
		#kwargs['context'] = context
		return fn(self, context, *args, **kwargs)

	return wrapper