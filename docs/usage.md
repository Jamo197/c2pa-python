# Using the Python library

This package works with media files in the [supported formats](https://github.com/contentauth/c2pa-rs/blob/main/docs/supported-formats.md).

## Import

Import the API as follows:

```py
from c2pa import *
```

## Define manifest JSON

The Python library works with both file-based and stream-based operations.
In both cases, the manifest JSON string defines the C2PA manifest to add to an asset; for example:

```py
manifest_json = json.dumps({
    "claim_generator": "python_test/0.1",
    "assertions": [
    {
      "label": "c2pa.training-mining",
      "data": {
        "entries": {
          "c2pa.ai_generative_training": { "use": "notAllowed" },
          "c2pa.ai_inference": { "use": "notAllowed" },
          "c2pa.ai_training": { "use": "notAllowed" },
          "c2pa.data_mining": { "use": "notAllowed" }
        }
      }
    }
  ]
 })
```

## Signing function

The `sign_ps256` function is [defined in the library](https://github.com/contentauth/c2pa-python/blob/main/c2pa/c2pa_api/c2pa_api.py#L209) is used in both file-based and stream-based methods and is reproduced here to show how signing is performed.

```py
# Example of using Python crypto to sign data using openssl with Ps256
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def sign_ps256(data: bytes, key_path: str) -> bytes:
    with open(key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature
```

## File-based operation

### Read and validate C2PA data

Use the `Reader` to read C2PA data from the specified asset file. 

This examines the specified media file for C2PA data and generates a report of any data it finds. If there are validation errors, the report includes a `validation_status` field.

An asset file may contain many manifests in a manifest store. The most recent manifest is identified by the value of the `active_manifest` field in the manifests map. The manifests may contain binary resources such as thumbnails which can be retrieved with `resource_to_stream` or `resource_to_file` using the associated `identifier` field values and a `uri`.

NOTE: For a comprehensive reference to the JSON manifest structure, see the [Manifest store reference](https://opensource.contentauthenticity.org/docs/manifest/manifest-ref).

```py
try:
  # Create a reader from a file path
  reader = c2pa.Reader.from_file("path/to/media_file.jpg")

  # Print the JSON for a manifest. 
  print("manifest store:", reader.json())

  # Get the active manifest.
  manifest = reader.get_active_manifest()
  if manifest != None:

    # get the uri to the manifest's thumbnail and write it to a file
    uri = manifest["thumbnail"]["identifier"]
    reader.resource_to_file(uri, "thumbnail_v2.jpg") 

except Exception as err:
    print(err)
```

### Add a signed manifest

**WARNING**: This example accesses the private key and security certificate directly from the local file system.  This is fine during development, but doing so in production may be insecure. Instead use a Key Management Service (KMS) or a hardware security module (HSM) to access the certificate and key; for example as show in the [C2PA Python Example](https://github.com/contentauth/c2pa-python-example).

Use a `Builder` to add a manifest to an asset:

```py
try:
  # Define a function to sign the claim bytes
  # In this case we are using a pre-defined sign_ps256 method, passing in our private cert
  # Normally this cert would be kept safe in some other location
  def private_sign(data: bytes) -> bytes:
    return sign_ps256(data, "tests/fixtures/ps256.pem")

  # read our public certs into memory
  certs = open(data_dir + "ps256.pub", "rb").read()

  # Create a signer from the private signer, certs and a time stamp service url
  signer = create_signer(private_sign, SigningAlg.PS256, certs, "http://timestamp.digicert.com")

  # Create a builder add a thumbnail resource and an ingredient file.
  builder = Builder(manifest_json)

  # The uri provided here "thumbnail" must match an identifier in the manifest definition.
  builder.add_resource_file("thumbnail", "tests/fixtures/A_thumbnail.jpg")

  # Define an ingredient, in this case a parent ingredient named A.jpg, with a thumbnail
  ingredient_json = {
    "title": "A.jpg",
    "relationship": "parentOf", # "parentOf", "componentOf" or "inputTo"
    "thumbnail": {
        "identifier": "thumbnail",
        "format": "image/jpeg"
    }
  }

  # Add the ingredient to the builder loading information  from a source file.
  builder.add_ingredient_file(ingredient_json, "tests/fixtures/A.jpg")

  # At this point we could archive or unarchive our Builder to continue later.
  # In this example we use a bytearray for the archive stream.
  # all ingredients and resources will be saved in the archive
  archive = io.BytesIO(bytearray())
  builder.to_archive(archive)
  archive.seek()
  builder = builder.from_archive(archive)

  # Sign and add our manifest to a source file, writing it to an output file.
  # This returns the binary manifest data that could be uploaded to cloud storage.
  c2pa_data = builder.sign_file(signer, "tests/fixtures/A.jpg", "target/out.jpg")

except Exception as err:
    print(err)
```

## Stream-based operation

Instead of working with files, you can read, validate, and add a signed manifest to streamed data.  This example code does the same thing as the file-based example.

### Read and validate C2PA data

```py
try:
  # It's also possible to create a reader from a format and stream
  # Note that these two readers are functionally equivalent
  stream = open("path/to/media_file.jpg", "rb")
  reader = c2pa.Reader("image/jpeg", stream)

  # Print the JSON for a manifest. 
  print("manifest store:", reader.json())

  # Get the active manifest.
  manifest = reader.get_active_manifest()
  if manifest != None:

    # get the uri to the manifest's thumbnail and write it to a file
    uri = manifest["thumbnail"]["identifier"]
    reader.resource_to_file(uri, "thumbnail_v2.jpg") 

except Exception as err:
    print(err)
```

### Add a signed manifest to a stream

**WARNING**: This example accesses the private key and security certificate directly from the local file system.  This is fine during development, but doing so in production may be insecure. Instead use a Key Management Service (KMS) or a hardware security module (HSM) to access the certificate and key; for example as show in the [C2PA Python Example](https://github.com/contentauth/c2pa-python-example).

Use a `Builder` to add a manifest to an asset:

```py
try:
  # Define a function to sign the claim bytes
  # In this case we are using a pre-defined sign_ps256 method, passing in our private cert
  # Normally this cert would be kept safe in some other location
  def private_sign(data: bytes) -> bytes:
    return sign_ps256(data, "tests/fixtures/ps256.pem")

  # read our public certs into memory
  certs = open(data_dir + "ps256.pub", "rb").read()

  # Create a signer from the private signer, certs and a time stamp service url
  signer = create_signer(private_sign, SigningAlg.PS256, certs, "http://timestamp.digicert.com")

  # Create a builder add a thumbnail resource and an ingredient file.
  builder = Builder(manifest_json)

  # Add the resource from a stream
  a_thumbnail_jpg_stream = open("tests/fixtures/A_thumbnail.jpg", "rb")
  builder.add_resource("image/jpeg", a_thumbnail_jpg_stream)

  # Define an ingredient, in this case a parent ingredient named A.jpg, with a thumbnail
  ingredient_json = {
    "title": "A.jpg",
    "relationship": "parentOf", # "parentOf", "componentOf" or "inputTo"
    "thumbnail": {
        "identifier": "thumbnail",
        "format": "image/jpeg"
    }
  }

  # Add the ingredient from a stream
  a_jpg_stream = open("tests/fixtures/A.jpg", "rb")
  builder.add_ingredient("image/jpeg", a_jpg_stream)

  # At this point we could archive or unarchive our Builder to continue later.
  # In this example we use a bytearray for the archive stream.
  # all ingredients and resources will be saved in the archive
  archive = io.BytesIO(bytearray())
  builder.to_archive(archive)
  archive.seek()
  builder = builder.from_archive(archive)

  # Sign the builder with a stream and output it to a stream
  # This returns the binary manifest data that could be uploaded to cloud storage.
  input_stream = open("tests/fixtures/A.jpg", "rb")
  output_stream = open("target/out.jpg", "wb")
  c2pa_data = builder.sign(signer, "image/jpeg", input_stream, output_stream)

except Exception as err:
    print(err)
 ```
