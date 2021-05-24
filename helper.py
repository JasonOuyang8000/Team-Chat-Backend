class tools():
  
    def get_token(header):
        PREFIX = 'Bearer '
        if not header.startswith(PREFIX):
            raise ValueError('Invalid token')

        return header[len(PREFIX):]