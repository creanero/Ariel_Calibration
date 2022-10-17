import pandas as pd
import matplotlib.pyplot as plt

# reads files structured in the format we're using for ariel files
def read_ariel(prompt):
    # loop until the user enters a correct filename
    while True:
        # asks the user to enter a file as prompted
        full_prompt = "Please enter the path to the " + prompt + " file:\t"
        filename = input(full_prompt)

        try:
            # reads the data into a pandas dataframe
            data= pd.read_csv(filename,
                              delim_whitespace=True, # files are delimted by whitespace (5 spaces)
                              header=None, # files have no headers
                              names=('Wavelength', 'Current', 'Control')) # files contain wavelength and current.
            break # end the loop if it worked correctly.

        # if the file isn't found
        except FileNotFoundError:
            print("File "+filename+" not found.")
            print("Please try again")

        #if the data can't be parsed into the 3-column structure we expect
        except pd.errors.ParserError:
            print("Unable to extract data from "+filename)
            print("Data in this file probably has the wrong structure")
            print("Please try again")

    return (data) # returns a pandas dataframe containing three columns

def read_dark():
    # describes the data to the user
    dark_name="Dark Current"

    # prompts the user for the file and reads it in
    dark_data=read_ariel(dark_name)

    # gets the average of the current values
    dark_average=dark_data['Current'].mean()

    return (dark_average)

def remove_dark(raw_data,dark=0.0):
    # copies the raw data
    data=raw_data.copy()

    #subtracts the dark current from it
    data["Current"]=data["Current"].sub(dark)
    return data

def extract_dark(prompt,dark):
    # prompts the user for the file and reads it in
    raw_data=read_ariel(prompt)

    #performs dark removal on
    data=remove_dark(raw_data,dark)
    return data


def calculate_transmission(unfiltered,filtered):
    merge_df=pd.merge(unfiltered,filtered, on="Wavelength", how='inner',suffixes=('_unfiltered','_filtered'))
    transmission_data=merge_df['Current_filtered']/merge_df['Current_unfiltered']
    transmission=pd.DataFrame({'Transmission':transmission_data,'Wavelength':merge_df['Wavelength']})

    return(transmission)

def plot_data(transmission):
    plt.plot(transmission['Wavelength'],transmission['Transmission'], 'k.')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Transmission')
    plt.title('Plot of Transmission against Wavelength')
    plt.show()


def save_data(transmission):
    pass


def main():
    # reads in the dark current values and return the average
    dark=read_dark()

    # reads in unfiltered data per frequency
    unfiltered=extract_dark("Unfiltered",dark)

    # reads in filtered data per frequency
    filtered=extract_dark("Filtered",dark)

    # Calculates the transmission (filtered/unfiltered)
    transmission=calculate_transmission(unfiltered,filtered)

    # Plots the data on a graph
    plot_data(transmission)

    # saves the transmission data
    save_data(transmission)



if __name__ == '__main__':
    main()

