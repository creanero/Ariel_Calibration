import pandas as pd
import matplotlib.pyplot as plt
import os

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


    print("Average Dark Current: "+f'{dark_average:.4g}'+" Amps")
    return (dark_average)

def remove_dark(raw_data,dark=0.0):
    # copies the raw data
    data=raw_data.copy()

    #subtracts the dark current from it
    data["Current"]=data["Current"].sub(dark)
    return data

def extract_dark(prompt,dark):
    # asks how many files to input
    count = ask_count("How many "+prompt+" files do you wish to input?")

    data_all = pd.DataFrame(columns=['Wavelength', 'Current'])
    for i in range(count):

        # prompts the user for the file and reads it in
        raw_data_i=read_ariel(to_ordinal(1+i)+" "+prompt)

        # performs dark removal on the data
        data_i=remove_dark(raw_data_i,dark)

        data_all=pd.concat([data_all,data_i])
    print("data_all")
    print(data_all)
    data=data_all.groupby('Wavelength', as_index=False)['Current'].mean()
    print("data")
    print(data)
    return data

def to_ordinal(in_integer):
    if in_integer in (11,12,13):
        out_ordinal = str(in_integer)+'th'
    elif 1 == in_integer%10:
        out_ordinal = str(in_integer)+'st'
    elif 2 == in_integer%10:
        out_ordinal = str(in_integer)+'nd'
    elif 3 == in_integer%10:
        out_ordinal = str(in_integer)+'rd'
    else:
        out_ordinal = str(in_integer)+'th'
    return out_ordinal
def ask_count(prompt='Please Enter an integer:'):
    count = 0
    while True:
        text_input=input(prompt+'\t')
        try:
            count = int(text_input)
            break

        except ValueError:
            print("WARNING: input value ("+text_input+") is not an integer!")
            print("Please try again.")

    return count



def calculate_transmission(unfiltered,filtered):
    merge_df=pd.merge(unfiltered,filtered, on="Wavelength", how='inner',suffixes=('_unfiltered','_filtered'))
    transmission_data=merge_df['Current_filtered']/merge_df['Current_unfiltered']
    transmission=pd.DataFrame({'Transmission':transmission_data,'Wavelength':merge_df['Wavelength']})

    return(transmission)

def plot_data(transmission):
    if 'y' == ask_yn("Plot the data on a graph"):
        plt.plot(transmission['Wavelength'],transmission['Transmission'], 'k.')
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Transmission')
        plt.title('Plot of Transmission against Wavelength')
        plt.show()

def ask_yn(prompt):
    while True:
        ans_yn=input('Do you wish to '+prompt+'? (y/n): \t')
        if ans_yn.lower() in ('y','yes', 'yeah', 'yep', 'yus', 'yarp'):
            ans_yn = 'y'
            break
        elif ans_yn.lower() in ('n','no', 'nah', 'nope', 'narp'):
            ans_yn = 'n'
            break
        else:
            print("Invalid response: "+ans_yn)

    return ans_yn

def get_save_path():
    while True: # repeat until it works
        filename = input("Please enter the file path to save to:\t")
        dirname = os.path.dirname(filename)
        if os.path.exists(filename): # if the file already exists
            print("WARNING: "+filename+" exists already!") # warn the user
            if 'y'==ask_yn("Overwrite "+filename): # check if they want to overwrite
                break # if they do, break the while loop and return the path
            else: # if they don't want to overwrite
                print("Select a new file") # tell them to try again, don't break the loop

        elif ''==dirname: # if the path is a relative path
            break # break the loop and return the filename

        elif os.path.exists(dirname): # if the directory exists (but not the file)
            break # break the loop and return the filename

        else: # if neither the file nor the directory exists and the path isn't relative
            try: # try to make the directory
                os.mkdir(dirname) # make the directory
                break # break the main loop and return the filename
            except OSError: # if it doesn't work
                print("ERROR: unable to create directory "+dirname)
                print("Please try again.") # warn the user, and allow them to try again

    return (filename)

def save_data(transmission):
    save_yn=ask_yn("save the transmission data")
    if 'y'==save_yn:
        while True:
            filename=get_save_path()
            try:
                transmission.to_csv(filename, index=False)
                break
            except OSError:
                print('Unable to save')

def read_data():
    # reads in the dark current values and return the average
    dark=read_dark()

    # reads in unfiltered data per frequency
    unfiltered=extract_dark("Unfiltered",dark)

    # reads in filtered data per frequency
    filtered=extract_dark("Filtered",dark)

    return(unfiltered,filtered)



def main():
    #read in the data
    unfiltered, filtered = read_data()

    # Calculates the transmission (filtered/unfiltered)
    transmission=calculate_transmission(unfiltered,filtered)

    # Plots the data on a graph
    plot_data(transmission)

    # saves the transmission data
    save_data(transmission)



if __name__ == '__main__':
    main()

