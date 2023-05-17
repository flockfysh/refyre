Implementation-wise, the "refactoring" capabilities of refyre go as follows:

-- The Why -- 

1. Integratability / Compatibility
    - People can just provide a refyre spec, and that will allow flockfysh to get all of the key information it needs to do it's job
        - Reduces the need for us to need to "force" the user into adopting / having to learn a format
        - Automatically upload & download data to and from pre-planned places without a hassle
            - flockfysh CLI can use this to ferry data to and from the user

2. Efficiency
    - Provides an easy python way to jump/edit/add/delete between file structures
    - Easy way to extract files
    - ** ENABLES US TO PROVIDE CUSTOM PIPELINES - WE DON'T NEED TO CARE ABOUT THE DIRECTORY STRUCTURE OF THE USER ** 

3. Progress
    - As a tool, we can also share this with researchers & companies
        - note: for commercial (profitable) use - we charge a small licencing fee
        - gets us connections and starts setting up pipelines that we can use for the future

Bottom Line: It's a simple, open-sourceable project that really just needs a bit of hairy Python. It's vital for flockfysh to make life easier for users, and not to have to be forced to one format

Higher Level Process:
1. Being able to read in / parse an input refyre spec
2. Being able to read in / parse what the OUTPUT structure should look like 
3. Adjust the original spec to the new spec

Clearly, there are two major processes being listed here:
    - Parsing an input spec 
    - Converting between a current spec to a desired spec

Ideally, some sort of method to verify the validity of an input spec would also be ideal. It would be necessary to maintain that
the graphs constructed by these methods shouldn't reference the validity method at all - it's goal is to simply construct the graph.

-- What additional features will be included? --
    - Retrieving / Aggregating specific data 
        - Will be based on regex / patterns (all images with "image___1___")
        - "variables" can be defined & aggregated to return a FileCluster() object, which then will have a variety of attributes / features that can be leveraged, including:
            1. Uploading (sending all the files into a GET/POST request, etc)
            2. Downloading
                - Zipping / Compressing all of this data
                - Downloading specific files
            3. Moving / Shifting the data around
                - Copy 
                - Cut 
                - Move 

---  General --- 
How it'll work:
    1. Create a file graph based on the directories listed in the refyre spec. 
        - Only directories listed in the refyre spec will be considered at all
    2. Leverage the file / graph structure to access the file data
        - Done through DFS
    

--- Post-Skeleton Steps --- 
    - Make it as humanly editable as possible!!!

    - Solid focus on integrating more "expansive features"
        - Pandas Support 
            - Constructing graphs for all files from pandas, etc. 
            - Saving filepaths directly to a df / df column

    - More Python-y support (distant future)
        - Code repository support  
            - Maintaining Python path support 
            - Cloning in Git repositories, and adding them to path
                - Essentially, user can list all repos on the spec 

            - Handling
            