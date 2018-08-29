from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager()

    builder.add(settings={"compiler": "clang",
                          "compiler.version": "6.0",
                          "compiler.libcxx": None,                          
                          "os": "Android",
                          "os.api_level": "21",
                          "arch": "armv7",
                          "build_type": "Release"})   

    builder.add(settings={"compiler": "clang",
                          "compiler.version": "6.0",
                          "compiler.libcxx": None,
                          "os": "Android",
                          "os.api_level": "21",
                          "arch": "armv8",
                          "build_type": "Release"})   

    builder.add(settings={"compiler": "clang",
                          "compiler.version": "6.0",
                          "compiler.libcxx": None,                          
                          "os": "Android",
                          "os.api_level": "21",
                          "arch": "x86",
                          "build_type": "Release"})   

    builder.add(settings={"compiler": "clang",
                          "compiler.version": "6.0",
                          "compiler.libcxx": None,
                          "os": "Android",
                          "os.api_level": "21",
                          "arch": "x86_64",
                          "build_type": "Release"})   
    builder.run()
