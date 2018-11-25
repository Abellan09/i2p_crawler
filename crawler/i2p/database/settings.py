# Node status and type constants
# NODE STATUS
NS_COD_ONGOING = 'O'
NS_COD_FINISHED = 'F'
NS_COD_PENDING = 'P'
NS_COD_NOTCRAWLEABLE = 'NC'
# {type:description}
NS_DEFAULT_INFO = {NS_COD_ONGOING:'O (Ongoing): The site is being crawled',
                   NS_COD_FINISHED:'F (Finished): The site has been successfully crawled',
                   NS_COD_PENDING:'P (Pending): The site is waiting to be launched again. May there was a processing error.',
                   NS_COD_NOTCRAWLEABLE:'NC (Not Crawleable): The site cannot be crawled'}

# NODE TYPE
NT_COD_I2P = 'I2P'
NT_COD_TOR = 'TOR'
NT_COD_SURFACE = 'WEB'
#{type:description}
NT_DEFAULT_INFO = {NT_COD_I2P:'I2P eepsite',
                   NT_COD_TOR:'TOR onion site',
                   NT_COD_SURFACE:'Surface web site'}