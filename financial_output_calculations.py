#Python class to read excel data containing financial bond details, creates cash flow, calculates EIR
#and then calculated amortised cost for a given date

import pandas as pd
from datetime import datetime



class XirrNpvCalBulk:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = pd.read_excel(self.filepath)

    def generate_pay_prof(self):
        total_profile = []
        for i in range(0,len(self.df)):
            start = self.df.iloc[i]['start_date']
            end = self.df.iloc[i]['end_date']
            coupon = self.df.iloc[i]['coupon']
            principal = self.df.iloc[i]['initial_principal']
            redemption = self.df.iloc[i]['redemption_amount']

            payments = [-principal, coupon*principal]
            pay_dates = [start.to_pydatetime(), (start+pd.DateOffset(months=2) +pd.tseries.offsets.MonthEnd(1)).to_pydatetime()]
            while pay_dates[-1] < end:
                new_date = pay_dates[-1]
                new_date = (new_date + pd.DateOffset(months=3) +pd.tseries.offsets.MonthEnd(0))
                pay_dates.append(new_date.to_pydatetime())

                payments.append(coupon*principal)
            payments[-1] = (coupon*principal + redemption)
            total_profile.append(list(zip(pay_dates, payments)))
        return total_profile

    def xirr(self):
        xirr_list = []
        transactions = self.generate_pay_prof()
        for y in range(0,len(self.df)):
            years = [(ta[0] - transactions[y][0][0]).days / 365.0 for ta in transactions[y]]
            residual = 1
            step = 0.05
            guess = 0.05
            epsilon = 0.0001
            limit = 10000
            while abs(residual) > epsilon and limit > 0:
                limit -= 1
                residual = 0.0
                for i, ta in enumerate(transactions[y]):
                    residual += ta[1] / pow(guess, years[i])
                if abs(residual) > epsilon:
                    if residual > 0:
                        guess += step
                    else:
                        guess -= step
                        step /= 2.0
            xirr_list.append(guess-1)
        return xirr_list

    def xnpv(self, eval_date):
        total_npv_list = []
        data_listing = self.generate_pay_prof()
        #NEED TO BE ONLY AFTER THE EVAL DATE
        for y in range(0,len(self.df)):
            npv_list = []
            for i in range(0,len(data_listing[y])):
                rate = self.xirr()[y]
                lag = ((data_listing[y][i][0] - eval_date).days/365)
                pv_of_pay= data_listing[y][i][1] / (1+rate)**lag
                npv_list.append(pv_of_pay)
            total_npv_list.append(npv_list)
            self.total_npv_list = total_npv_list
        return self.total_npv_list

    def create_table(self, eval_date):
        df1 = pd.DataFrame(self.xnpv(eval_date))
        df2 = pd.DataFrame(self.generate_pay_prof())
        df3 = pd.DataFrame(self.xirr())
        frames = [df1, df2, df3]
        result = pd.concat(frames)
        return result.to_csv()

    def do_anything(self):
        return self.df.to_csv('')







class XirrNpvCalOne:
    def __init__(self, start, end, coupon, principal, redemption):
        self.start = pd.Timestamp(datetime.strptime(start, "%Y-%m-%d"))
        self.end = pd.Timestamp(datetime.strptime(end, "%Y-%m-%d"))
        self.coupon = float(coupon)
        self.principal = int(principal)
        self.redemption = int(redemption)

    def generate_pay_prof(self):
        total_profile = []
        payments = [-self.principal, self.coupon*self.principal]
        pay_dates = [self.start.to_pydatetime(), (self.start+pd.DateOffset(months=2) +pd.tseries.offsets.MonthEnd(1)).to_pydatetime()]
        while pay_dates[-1] < self.end:
            new_date = pay_dates[-1]
            new_date = (new_date + pd.DateOffset(months=3) +pd.tseries.offsets.MonthEnd(0))
            pay_dates.append(new_date.to_pydatetime())
            payments.append(self.coupon*self.principal)
        payments[-1] = (self.coupon*self.principal + self.redemption)
        total_profile.append(list(zip(pay_dates,payments)))
        return total_profile[0]

    def xirr(self):
        xirr_list = []
        transactions = self.generate_pay_prof()
        years =  years = [(ta[0] - transactions[0][0]).days / 365.0 for ta in transactions]
        residual = 1
        step = 0.05
        guess = 0.05
        epsilon = 0.0001
        limit = 10000
        while abs(residual) > epsilon and limit > 0:
            limit -= 1
            residual = 0.0
            for i, ta in enumerate(transactions):
                residual += ta[1] / pow(guess, years[i])
            if abs(residual) > epsilon:
                if residual > 0:
                    guess += step
                else:
                    guess -= step
                    step /= 2.0
        xirr_list.append(guess-1)
        return xirr_list[0]

    def xnpv(self, eval_date):
        eval_date = datetime.strptime(eval_date, "%Y-%m-%d")
        data_listing = self.generate_pay_prof()
        #NEED TO BE ONLY AFTER THE EVAL DATE
        npv_list = []
        rate = self.xirr()
        for i in range(0,len(data_listing)):
                       lag = ((data_listing[i][0] - eval_date).days/365)
                       pv_of_pay= data_listing[i][1] / (1+rate)**lag
                       npv_list.append(pv_of_pay)
        profile = (zip(npv_list, data_listing))
        total = []
        for i in profile:
            if i[1][0] >= eval_date:
                total.append(i[0])

        return sum(total)
