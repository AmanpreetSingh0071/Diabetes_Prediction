# -*- coding: utf-8 -*-
"""Diabetes_prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1POWK1YnXhUDQ8A9gbxuQR9dzFXagmdsg
"""

! pip install pyspark

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('spark').getOrCreate()

! git clone https://github.com/education454/diabetes_dataset

! ls diabetes_dataset

df = spark.read.csv('/content/diabetes_dataset/diabetes.csv', header=True, inferSchema=True)

df.show()

df.printSchema()

print((df.count(),len(df.columns)))

df.groupby('Outcome').count().show()

df.describe().show()

for col in df.columns:
  print(col+":",df[df[col].isNull()].count())

def count_zeros():
  columns_list = ['Glucose','BloodPressure','SkinThickness','Insulin','BMI']
  for i in columns_list:
    print(i+":",df[df[i]==0].count())

count_zeros()

from pyspark.sql.functions import *
for i in df.columns[1:6]:
  data = df.agg({i:'mean'}).first()[0]
  print("mean value for {} is {}".format(i,int(data)))
  df = df.withColumn(i,when(df[i]==0,int(data)).otherwise(df[i]))

df.show()

for col in df.columns:
  print("correlation to outcome for {} is {}".format(col,df.stat.corr('Outcome',col)))

from pyspark.ml.feature import VectorAssembler
assembler = VectorAssembler(inputCols=['Pregnancies','Glucose','BloodPressure','SkinThickness','Insulin','BMI','DiabetesPedigreeFunction','Age'],outputCol='features')
output_data = assembler.transform(df)

output_data.printSchema()

output_data.show()

from pyspark.ml.classification import LogisticRegression
final_data = output_data.select('features','Outcome')

final_data.printSchema()

train , test = final_data.randomSplit([0.7,0.3])
models = LogisticRegression(labelCol='Outcome')
model = models.fit(train)

summary = model.summary

summary.predictions.describe().show()

from pyspark.ml.evaluation import BinaryClassificationEvaluator
predictions = model.evaluate(test)

predictions.predictions.show(50)

evaluator = BinaryClassificationEvaluator(rawPredictionCol='rawPrediction',labelCol='Outcome')
evaluator.evaluate(model.transform(test))

model.save("Diabetes_model")

from pyspark.ml.classification import LogisticRegressionModel
model = LogisticRegressionModel.load('Diabetes_model')

