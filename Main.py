import numpy as np
import datetime
import pandas as pd
from sklearn import linear_model

from tkinter import *
from tkinter import ttk
import tkinter.font as font
from tkinter import messagebox



train_data = pd.read_csv('train-data.csv')

# Removing the first indexing column
train_data = train_data.iloc[:,1:]

# Removing null values from some columns
train_data = train_data[train_data['Mileage'].notna()]
train_data = train_data[train_data['Engine'].notna()]
train_data = train_data[train_data['Power'].notna()]
train_data = train_data[train_data['Seats'].notna()]
train_data = train_data.reset_index(drop=True)

# Removing Units from values 
for i in range(train_data.shape[0]):
    train_data.at[i, 'Company'] = train_data['Name'][i].split()[0]
    train_data.at[i, 'Mileage(km/kg)'] = train_data['Mileage'][i].split()[0]
    train_data.at[i, 'Engine(CC)'] = train_data['Engine'][i].split()[0]
    train_data.at[i, 'Power(bhp)'] = train_data['Power'][i].split()[0]

# Converting values to float
train_data['Mileage(km/kg)'] = train_data['Mileage(km/kg)'].astype(float)
train_data['Engine(CC)'] = train_data['Engine(CC)'].astype(float)


count = 0
position = []
for i in range(train_data.shape[0]):
    if train_data['Power(bhp)'][i]=='null':
        count = count + 1
        position.append(i)

        
train_data = train_data.drop(train_data.index[position])
train_data = train_data.reset_index(drop=True)

train_data['Power(bhp)'] = train_data['Power(bhp)'].astype(float)

for i in range(train_data.shape[0]):
    if pd.isnull(train_data.loc[i,'New_Price']) == False:
        train_data.at[i,'New_car_Price'] = train_data['New_Price'][i].split()[0]
        
train_data['New_car_Price'] = train_data['New_car_Price'].astype(float)


# Droping the columns which are not needed
train_data.drop(["Name"],axis=1,inplace=True)
train_data.drop(["Mileage"],axis=1,inplace=True)
train_data.drop(["Engine"],axis=1,inplace=True)
train_data.drop(["Power"],axis=1,inplace=True)
train_data.drop(["New_Price"],axis=1,inplace=True)


# Owner type - string to number
train_data.replace({"First":1,"Second":2,"Third": 3,"Fourth & Above":4},inplace=True)

train_data.drop(["Company"],axis=1,inplace=True)


# Getting the different Location in the data and making column of each 
var = 'Location'
Location = train_data[[var]]
Location = pd.get_dummies(Location,drop_first=True)

# Getting the different Fuel Types in the data and making column of each
var = 'Fuel_Type'
Fuel_t = train_data[[var]]
Fuel_t = pd.get_dummies(Fuel_t,drop_first=True)

# Getting the different Transmission Types in the data and making column of each
var = 'Transmission'
Transmission = train_data[[var]]
Transmission = pd.get_dummies(Transmission,drop_first=True)


# Final data -
final_train= pd.concat([train_data,Location,Fuel_t,Transmission],axis=1)


# Linear Regression - y= m1x1 + m2x2 + ... mnxn + C
# X = Independent variable
X = final_train.loc[:,['Year', 'Kilometers_Driven', 'Owner_Type', 'Seats',
       'Mileage(km/kg)', 'Engine(CC)', 'Power(bhp)', 
       'Location_Bangalore', 'Location_Chennai', 'Location_Coimbatore',
       'Location_Delhi', 'Location_Hyderabad', 'Location_Jaipur',
       'Location_Kochi', 'Location_Kolkata', 'Location_Mumbai',
       'Location_Pune', 'Fuel_Type_Diesel', 'Fuel_Type_LPG',
       'Fuel_Type_Petrol', 'Transmission_Manual']]
# y = Dependent Variable
y = final_train.loc[:,['Price']]

model = linear_model.LinearRegression()
# Passing the values of X and y in Linear Regression Model
model.fit(X,y)

# Getting the Coefficients and Intercept
coef = model.coef_             # coefficients(m1,m2,....,mn)
intercept = model.intercept_   # intercept(C)


# getting coeffiecients in one dimension
coefficient = []
for i in coef[0]:
    coefficient.append(i)
    

# Getting All Locations and All Fuel types from dataset in tuple to show in gui
all_Locations = [i[9:] for i in Location.columns]
all_fuel = [i[10:] for i in Fuel_t.columns]
all_fuel = tuple(all_fuel)
all_Locations = tuple(all_Locations)



# ==========Functions to calculate Price===================

def estimate():
	# if car is older than 15 years(can't sell) or year is more than current year
    curYear = datetime.datetime.now().year
    age = curYear-yearVar.get()
    if(age > 15 or age<0 ):
        return 0;
    
    # Getting Location of car to give that location coefficient to price
    loc = city.get()
    cityTotal =0
    for i in range(len(all_Locations)):
        if all_Locations[i] == loc:
            cityTotal = coefficient[i+7]
            break
    
    # Getting Fuel Type of car to give that location coefficient to price
    fuel_type = Fuel.get()
    fuel_total = 0
    for i in range(len(all_fuel)):
        if all_fuel[i] == fuel_type:
            fuel_total = coefficient[i+17]
            break
    
    # Price Calculation (y = m1x1 + m2x2 + ... + c)
    y = ( yearVar.get()*coefficient[0]+kmVar.get()*coefficient[1] + (owner.current() +1)*coefficient[2] + seatVar.get()*coefficient[3] + 
    	engineVar.get()*coefficient[5] + mileageVar.get()*coefficient[4] +powerVar.get()*coefficient[6] + cityTotal + fuel_total+
    	trans.current()*coefficient[20] + intercept[0] )
    return y


  
def prediction(l):
	# Some compulsory values, if not give then show error
    if(yearVar.get()==0 or seatVar.get()==0 or Fuel.current()==-1 or trans.current()== -1 or city.current()==-1 or owner.current()==-1):
        messagebox.showerror("Error", "Values are missing")
        return
    

    frame1.place_forget()
    frame2 = Frame(win,bg='#557bc2')
    frame2.place(x=0,y=0,width=530,height = 500)
    
    # Back Button Function for frame2
    def goBack():
        frame2.place_forget()
        frame1.place(x=0,y=0,width=530,height = 500)
    
    # Calling estimate to get price
    price = estimate()
    output = "price"

    if(price == 0):
        output = "Your Car is Not under 15 Year Policy!!"
    elif(price < 0):
    	output = "Your Car is Not in condition to sell!!"
    else:
        price = '%.3f'%price
        output = f"Estimated Price is Rs. {price} Lakh"
    
    myfont2 = font.Font(size=15) # Font property
    tot = Label(frame2,text = output,fg='green',font=myfont2)
    tot.place(x=100,y=100)
    
    back = Button(frame2,text = "Back",font=myfont2,command = goBack)
    back.place(x=225,y=180)
    
     
    
# =======Tkinter Part========================


win = Tk()
win.geometry('530x500')
win.title("Price Estimation of Used Cars")
myfont = font.Font(size=10)

frame1 = Frame(win,bg='#557bc2')
frame1.place(x=0,y=0,width=530,height=500)



# YEAR 
yearVar = IntVar()

Year_l = Label(frame1,text="Year",bg='#557bc2',fg = 'white',font = myfont)
Year = Entry(frame1, textvariable = yearVar)
Year_l.place(x=15 , y=20)
Year.place(x=120 , y=20)

# Kilometer Driven
kmVar = DoubleVar()


km_l = Label(frame1,text = 'Kilometer Driven',bg='#557bc2',fg = 'white',font = myfont)
km = Entry(frame1, textvariable = kmVar)
km_l.place(x=265,y=20)
km.place(x=370,y=20)

# Mileage
mileageVar = DoubleVar()

Mileage_l = Label(frame1,text = 'Mileage(kmpl)',bg='#557bc2',fg = 'white',font = myfont)
Mileage = Entry(frame1, textvariable = mileageVar)
Mileage_l.place(x=15,y=50)
Mileage.place(x=120,y=50)

# Number of seats
seatVar = IntVar()

Seats_l = Label(frame1,text = 'No. Of Seats',bg='#557bc2',fg='white',font=myfont)
Seats = Entry(frame1, textvariable = seatVar)
Seats_l.place(x=265 , y=50)
Seats.place(x=370 , y=50)

# Engine(CC)
engineVar = DoubleVar()

cc_l = Label(frame1,text = 'Engine(cc)',bg='#557bc2',fg = 'white',font = myfont)
cc = Entry(frame1, textvariable = engineVar)
cc_l.place(x=15,y=80)
cc.place(x=120,y=80)

# Power(bhp)
powerVar = DoubleVar()

power_l = Label(frame1,text = "Power(bhp)",bg='#557bc2',fg = 'white',font=myfont)
power = Entry(frame1, textvariable = powerVar)
power_l.place(x=265,y=80)
power.place(x=370,y=80)

# Fuel Type
Fuel_l = Label(frame1,text = 'Fuel_type',bg='#557bc2',fg = 'white',font = myfont) 
Fuel = ttk.Combobox(frame1)
Fuel['values'] = all_fuel
Fuel.set('Select')
Fuel_l.place(x=15,y=120)
Fuel.place(x=120,y=120)


# Transmition Type
trans_l  = Label(frame1,text = "Transmition Type",bg='#557bc2',fg = 'white',font = myfont)
trans = ttk.Combobox(frame1)
trans['values'] = ('Automatic','Manual')
trans.set('Select')
trans_l.place(x=15,y=150)
trans.place(x=120,y=150)

# City
city_l = Label(frame1,text = "City",bg='#557bc2',fg = 'white',font = myfont)
city = ttk.Combobox(frame1)
city['values']= all_Locations
city.set('Select')
city_l.place(x = 15,y=180)
city.place(x=120,y=180)

# Owner
owner_l = Label(frame1,text = 'Owner Type',bg='#557bc2',fg = 'white',font = myfont)
owner = ttk.Combobox(frame1)
owner['values'] = ("Fist","Second","Third","Fourth & Above")
owner.set('Select')
owner_l.place(x=15,y=210)
owner.place(x=120,y=210)

l = [yearVar,kmVar,mileageVar,seatVar,engineVar,powerVar]

# Predict Button
predict = Button(frame1,text='PREDICT' , command=lambda: prediction(l))
predict.place(x=225,y=260)

win.mainloop()