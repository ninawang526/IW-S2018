import twitter

consumer_key         = "yicSg4MsxQHcegoyy80XXdWSE"
consumer_secret      = "ApbUm0xrOegvpJQuQbcCszHiiQ3cHE87ER2gcLUfPi8tpfYyfR"
access_token_key     = "173325385-c8fhGSRI9zEmRVsyhtQIttCWfVmLzZubVUGfWnKD"
access_token_secret  = "7yKdHCAk5PqlAhs7SeFnB61EP7yOS5o694ndt6ZXjlc2q"

api1 = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token_key,
                  access_token_secret=access_token_secret,
                  sleep_on_rate_limit=False)

consumer_key2 = "9PASS1v6kukRdjoO8IgOR9GGg"
consumer_secret2 = "	O90GaP4knytCYRNvAUYDK6qO63jyodSJWZOcizExqMcu3Oy1vh"
access_token_key2 = "173325385-6W9YJ2UJAhLiGT4rRYBzUOY1yAnDcXfMwjlutxBy"
access_token_secret2 = 	"jKyG0bUIg8Qf3KJNa5LTEWC8IBrZXESCXMYNsmysBIr54"


api2 = twitter.Api(consumer_key=consumer_key2,
                  consumer_secret=consumer_secret2,
                  access_token_key=access_token_key2,
                  access_token_secret=access_token_secret2,
                  sleep_on_rate_limit=False)

consumer_key3 = "pVp2EoaEfcZssEtV8ZkWcD1WG"
consumer_secret3 = "IXcGxjupX2sNRGmlp5W6ZzIPvRciSUhYomUakjSxJO7vKdLES9"
access_token_key3 = "173325385-fxoFxP9AtYpIpIcmxgTvnQvmL4RfqAoFLpG2IqlJ"
access_token_secret3 = "73DFwBTRs5SN3iTU1yJFtn2HGya75tpJwmaMKN8vCwmVT"

api3 = twitter.Api(consumer_key=consumer_key3,
                  consumer_secret=consumer_secret3,
                  access_token_key=access_token_key3,
                  access_token_secret=access_token_secret3,
                  sleep_on_rate_limit=False)


consumer_key4 = "anDGmgkMUoRbctp7UnYNmeJdn"
consumer_secret4 = "zPoVMDTsOx7Naw1MFI8SAEMIuroeKSYVmT8Ap8wVteMdE4uAER"
access_token_key4 = "173325385-KrXSFW4m0QtQ766XvpLDm40JfOkN8jfLRZMalvLS"
access_token_secret4 = "vPyWxZEMxLdXPQ8KbF1KfxAoMzT57LV7sJTNvoyn1qpx9"

api4 = twitter.Api(consumer_key=consumer_key4,
                  consumer_secret=consumer_secret4,
                  access_token_key=access_token_key4,
                  access_token_secret=access_token_secret4,
                  sleep_on_rate_limit=False)

consumer_key5 = "BTV3FkFDJgwYCI9dCznzy8H5B"
consumer_secret5 = "bijMU57ZgyB92ydeg3w5NJFnpJa4rx0dXibnFma2hJ3PH8QXXy"
access_token_key5 = "173325385-E3mCY1ZHwLYufkEtaVShxhpcu39wDgpkz2B69PLT"
access_token_secret5 = "sZvWZ3HNW8nrVHpuSKdNQk1Ux8nL4dJsIB53mCRwepBmZ"

api5 = twitter.Api(consumer_key=consumer_key5,
                  consumer_secret=consumer_secret5,
                  access_token_key=access_token_key5,
                  access_token_secret=access_token_secret5,
                  sleep_on_rate_limit=False)

consumer_key6 = "TMAGxvTYRRz26j9J1FRxZnU1Y"
consumer_secret6 = "xcqPwMk8pYNqHOf0PaGQKozFXXgGOTkR3NTBbjBMvkJDWiYQgd"
access_token_key6 = "173325385-kdqbecTxdrwzwCyQc1j0XQmcDhFGvjZGA4sinl1N"
access_token_secret6 = "zps4Ny1ySxESX0btL1qc4nOySjIhnZf143VivpcBAvcui"

api6 = twitter.Api(consumer_key=consumer_key6,
                  consumer_secret=consumer_secret6,
                  access_token_key=access_token_key6,
                  access_token_secret=access_token_secret6,
                  sleep_on_rate_limit=False)

apis = [api1, api2, api3, api4, api5, api6]

def getAPI(i):
      return apis[(i % len(apis))-1]





