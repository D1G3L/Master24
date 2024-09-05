import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats
from scipy.stats import pointbiserialr, friedmanchisquare

# To ensure the code runs smoothly, please install all the required packages using the following command:
# pip install pandas numpy seaborn matplotlib scipy statsmodels
#
# Additionally, this code was executed in an Anaconda environment with Python version 3.9.7

# read data
data = pd.read_csv('summary_acc_time_con.csv')
data_nasaTLX = pd.read_csv('summary_demand.csv')
merged_data = pd.merge(data, data_nasaTLX, on='ID')

print("--------------------------------Start Mean, Median, MAD--------------------------------\n")
# accuracy
accuracy_per_condition = data.groupby('condition')['correct'].mean()
print("accuracy per condition:")
print(accuracy_per_condition)

# response time mean and median
response_time_per_condition = data.groupby('condition')['response_time'].mean()
print("\nresponse time per condition - mean:")
print(response_time_per_condition)
response_time_per_condition = data.groupby('condition')['response_time'].median()
print("\nresponse time per condition - median:")
print(response_time_per_condition)
#  confidence mean and median
confidence_per_condition = data.groupby('condition')['confidence'].mean()
print("\nconfidence per condition - mean:")
print(confidence_per_condition)
confidence_per_condition = data.groupby('condition')['confidence'].median()
print("\nconfidence per condition - median:")
print(confidence_per_condition)

# response time and confidence mad
stats = merged_data.groupby('condition_x').agg({
    'response_time': [lambda x: np.mean(np.abs(x - np.mean(x)))],
    'confidence': [lambda x: np.mean(np.abs(x - np.mean(x)))],
})
stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
stats.rename(columns={
    'response_time_<lambda>': 'response_time_mad',
    'confidence_<lambda>': 'confidence_mad',
}, inplace=True)

print(stats)

# mental demand mean and median
mental_demand_per_condition = data_nasaTLX.groupby('condition')['mental_demand'].mean()
print("\nmental demand per condition - mean:")
print(mental_demand_per_condition)
mental_demand_per_condition = data_nasaTLX.groupby('condition')['mental_demand'].median()
print("\nmental demand per condition - median:")
print(mental_demand_per_condition)
# physical demand mean and median
physical_demand_per_condition = data_nasaTLX.groupby('condition')['physical_demand'].mean()
print("\nphysical demand per condition - mean:")
print(physical_demand_per_condition)
physical_demand_per_condition = data_nasaTLX.groupby('condition')['physical_demand'].median()
print("\nphysical demand per condition - median:")
print(physical_demand_per_condition)

# mental and physical demand mad
stats = merged_data.groupby('condition_y').agg({
    'physical_demand': [lambda x: np.mean(np.abs(x - np.mean(x)))],
    'mental_demand': [lambda x: np.mean(np.abs(x - np.mean(x)))]
})
stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
stats.rename(columns={
    'physical_demand_<lambda>': 'physical_demand_mad',
    'mental_demand_<lambda>': 'mental_demand_mad',
}, inplace=True)

print(stats)
print("--------------------------------End Mean, Median, MAD--------------------------------\n")

print("--------------------------------Start statistical tests--------------------------------\n")
# Friedman's ANOVA

# Friedman's ANOVA for accuracy
accuracy_data = data.groupby(['ID', 'condition'])['correct'].mean().unstack()
stat, p = friedmanchisquare(accuracy_data['rotation'], accuracy_data['step'], accuracy_data['swing'])
print(f"Friedman's ANOVA Test Statistics: {stat}")
print(f"p-Value: {p}")

# One-Way ANOVA 

# One-Way ANOVA for response time
model_response_time = ols('response_time ~ C(condition)', data=data).fit()
anova_response_time = sm.stats.anova_lm(model_response_time, typ=2)
print("\nOne-Way ANOVA for response time:")
print(anova_response_time)

# One-Way ANOVA for confidence
model_confidence = ols('confidence ~ C(condition)', data=data).fit()
anova_confidence = sm.stats.anova_lm(model_confidence, typ=2)
print("\nOne-Way ANOVA for confidence:")
print(anova_confidence)

# One-Way ANOVA for mental demand
model_mental = ols('mental_demand ~ C(condition)', data=data_nasaTLX).fit()
anova_mental = sm.stats.anova_lm(model_mental, typ=2)
print("\nOne-Way ANOVA for mental demand:")
print(anova_mental)

# One-Way ANOVA for physical demand
model_physical = ols('physical_demand ~ C(condition)', data=data_nasaTLX).fit()
anova_physical = sm.stats.anova_lm(model_physical, typ=2)
print("\nOne-Way ANOVA for physical demand:")
print(anova_physical)

# Post-hoc Test Tukey's HSD

# Tukey's HSD for response time
tukey_response_time = pairwise_tukeyhsd(endog=data['response_time'],
                                        groups=data['condition'],
                                        alpha=0.05)

print("\nPost-hoc Test Tukey's HSD for response time:")
print(tukey_response_time)

print("--------------------------------End statistical tests--------------------------------\n")

print("--------------------------------Start correlation tests--------------------------------\n")

# Correlation between confidence and response time
corr_confidence_rt = data[['confidence', 'response_time']].corr().iloc[0, 1]
print("\nCorrelation between confidence and response time:", corr_confidence_rt)

# Correlation between accuracy and confidence
corr_confidence_correct, p_value_accuracy_confidence = pointbiserialr(data['correct'], data['confidence'])
print(f"Correlation between accuracy and confidence: {corr_confidence_correct}")
print(f"p-Value: {p_value_accuracy_confidence}")

# Correlation between accuracy and mental demand
corr_mental, p_value_accuracy_mental = pointbiserialr(merged_data['correct'], merged_data['mental_demand'])
print(f"Correlation between accuracy and mental demand: {corr_mental}")
print(f"p-Value: {p_value_accuracy_mental}")

# Correlation between accuracy and physical demand
corr_physical, p_value_accuracy_physical = pointbiserialr(merged_data['correct'], merged_data['physical_demand'])
print(f"Correlation between accuracy and physical demand: {corr_physical}")
print(f"p-Value: {p_value_accuracy_physical}")

print("--------------------------------End correlation tests--------------------------------\n")

print("--------------------------------Start plot generation--------------------------------\n")

# boxplot - confidence by condition
sns.boxplot(x='condition', y='confidence', palette="colorblind", data=data, hue='condition', legend=False)
plt.title('Confidence by Condition')
plt.show()
# boxplot - response Time by condition
sns.boxplot(x='condition', y='response_time', palette="colorblind", data=data, hue='condition', legend=False)
plt.xlabel('condition')
plt.ylabel('response time')
plt.title('Response Time by Condition')
plt.show()
# barplot - mental demand by condition
sns.barplot(x='condition', y='mental_demand', palette="colorblind", data=data_nasaTLX, hue='condition', legend=False)
plt.xlabel('condition')
plt.ylabel('mental demand')
plt.title('NASA TLX Mental Demand Score per Condition')
plt.show()
# barplot - physical demand by condition
sns.barplot(x='condition', y='physical_demand', palette="colorblind", data=data_nasaTLX, hue='condition', legend=False)
plt.xlabel('condition')
plt.ylabel('physical demand')
plt.title('NASA TLX Physical Demand Score per Condition')
plt.show()
# boxplot - mental demand by condition
sns.boxplot(x='condition', y='mental_demand', palette="colorblind", data=data_nasaTLX, hue='condition', legend=False)
plt.xlabel('condition')
plt.ylabel('mental demand')
plt.title('NASA TLX Mental Demand Score per Condition')
plt.show()
# boxplot - physical demand by condition
sns.boxplot(x='condition', y='physical_demand', palette="colorblind", data=data_nasaTLX, hue='condition', legend=False)
plt.xlabel('condition')
plt.ylabel('physical demand')
plt.title('NASA TLX Physical Demand Score per Condition')
plt.show()
# scatterplot - correlation between confidence and response time
sns.scatterplot(x='response_time', y='confidence', data=data)
plt.xlabel('response time')
plt.ylabel('confidence')
plt.title('Correlation between Response Time and Confidence')
plt.show()
# boxplot - correlation between accuracy and confidence
sns.boxplot(x='correct', y='confidence', palette="colorblind", data=data, hue='correct', legend=False)
plt.xlabel('accuracy')
plt.ylabel('confidence')
plt.title('Correlation between Accuracy and Confidence')
plt.show()
# boxplot - correlation between accuracy and mental demand
sns.boxplot(x='correct', y='mental_demand', palette="colorblind", data=merged_data, hue='correct', legend=False)
plt.xlabel('correct')
plt.ylabel('mental demand')
plt.title('Correlation between Accuracy and Mental Demand')
plt.show()
# boxplot - correlation between accuracy and physical demand
sns.boxplot(x='correct', y='physical_demand', palette="colorblind", data=merged_data, hue='correct', legend=False)
plt.xlabel('correct')
plt.ylabel('physical demand')
plt.title('Correlation between Accuracy and Physical Demand')
plt.show()
print("--------------------------------End plot generation--------------------------------\n")