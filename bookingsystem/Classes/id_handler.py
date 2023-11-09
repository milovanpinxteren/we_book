from sqids import Sqids

class IDHandler():
    #uncomment this to generate ids
    # sqids = Sqids(alphabet="8yPqDhS3bLJzRg7N0sX6E2mW4A1iVvOoF5lUcT9xK", min_length=5)
    # for i in range(1, 900):
    #     id = sqids.encode([i])
    #     print(i, ',', id)

    def decode(self, id_code):
        sqids = Sqids(alphabet="8yPqDhS3bLJzRg7N0sX6E2mW4A1iVvOoF5lUcT9xK") #TODO: to env vars
        id = sqids.decode(id_code)[0]  # [1, 2, 3]
        return id

