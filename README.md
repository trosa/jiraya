# jiraya
Script to export issue transition data from Jira for lead time / throughput reporting purposes.

## Installation
Jiraya requires <code>python3</code> and <code>pip</code>.

If you're on a Mac, here's how to install those: https://docs.python-guide.org/starting/install3/osx/

1. Clone the repository into a local folder:

        git clone https://github.com/trosa/jiraya.git

2. Create a virtual environment within the project folder:

        python3 -m venv jiraya/venv
        
3. Activate the virtual environment:

        cd jiraya
        source venv/bin/activate
        
4. Install the dependencies from <code>requirements.txt</code> using pip:

        pip install -r requirements.txt
        
5. Create your own <code>config</code> file which will contain the information for your specific Jira instance:

        cp config.default config
        
6. Modify your new <code>config</code> file by adding your Jira URL, username, API key, and other configurations

7. Unleash the power of Jiraya!

        python3 jiraya.py
        
8. Jiraya will generate a CSV file named <code>output.csv</code> containing the data extracted from Jira