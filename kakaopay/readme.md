
# Regression-test code
[Test code of Boston Housing in Python](https://github.com/kim-taehee/Algorithm-code-in-Python/kakaopay/paytest2.ipynb)

## 1.데이터 전처리 및 속성별 확인 과정
Input : 'CRIM','ZN','INDUS','CHAS','NOX','RM','AGE','DIS','RAD','TAX','PTRATIO','B','LSTAT'  
Output : 'MEDV'

### 1-1. Histogram plot으로 변수별 분포 
    - 'CHAS,'B','CRIM,'ZN'의 네 가지 변수는 skewed data
    - normalize를 위해 log변환을 실시
    ![corr](https://user-images.githubusercontent.com/19430286/54505934-7be73380-497d-11e9-87e5-d7eb9973118a.png)

### 1-2. Corr,HeatMap으로 변수별 상관계수 확인
    - abs(0.7)이상의 상관계수를 보이는 col끼리 묶으면,  
      1st= RM,LSTAT,MEDV   2nd= INDUS,NOX,DIS,AGE,logZN   3nd= RAD,TAX,logCRIM 가 된다.  
    - 상관계수가 적은 'CRIM','ZN','CHAS','PTRATIO','B','logB' 는 삭제
    ![hm](https://user-images.githubusercontent.com/19430286/54505978-9ae5c580-497d-11e9-8362-e37543ca80c6.png)

### 1-3. 학습데이터셋과 검증데이터셋으로 분할


## 2.데이터 모델링

### 2-1. 머신러닝 모델
    - 회귀분석 기반 모델의 하이퍼파라미터들을 정의 : alpha
    - 여러 모델을 학습가능한 함수, def cv_mae() 작성 : CrossValidation(교차검증)시의 mae과, 테스트셋검증 mae_test을 리턴함
    - Ridge, Lasso, Elasticnet, SVR의 회귀기반 4개 모델과 lightGBM, GradientBoosting 트리기반 2개 모델로 학습
### 2-2. 딥러닝 모델
    - 딥러닝 회귀모형 함수 작성 
    - epoch=400, batch_size=10 으로 CrossValidation
    

## 3.모델 평가
    - cv_mae 함수를 실행하여, 모델별 MAE,Runtime 계산 
        ernel Ridge score: mean:3.8039 (std:0.7116)
         runntime: 0:00:02.674846
        Kernel Ridge pred-score: 3.6728388835300754 

        Lasso score: mean:3.8559 (std:0.6362)
         runntime 0:00:00.259306
        Lasso pred-score: 3.6199544948396616 

        ElasticNet score: mean:3.8550 (std:0.6364)
         runntime 0:00:00.955445
        ElasticNet pred-score:  3.620307935536951 

        SVR score: mean:4.9106 (std:0.8900)
         runntime 0:00:00.120677
        SVR pred-score: 4.289586755783465 

        Lightgbm score: mean:2.7052 (std:0.4196)
         runntime 0:00:07.384253
        Lightgbm pred-score: 2.351534105024359 

        GradientBoosting score: mean:2.3410 (std:0.2990)
         runntime 0:00:39.537265
        GradientBoosting pred-score: 1.9887824523369608 
        
        Deep learning score: 1.9012332918434056
         runntime
        Deep learning pred-score: 1.7739693303918833
        ![DL_rate](https://user-images.githubusercontent.com/19430286/54505987-a5a05a80-497d-11e9-8578-962c97d9bbe2.png)

      
## 결론
    - runtime 1초 이내에서는 ElasticNet이     최소 MAE=3.620  
    - runtime 8초 이내에서는 Lightgbm이       최소 MAE=2.351
    - runtime 40초 이내에서는 Deep learning이 최소 MAE=1.773 
    ※사용목적에 따라 알고리즘 선택필요
