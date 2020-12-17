import re
from django.db import models
from datetime import date
from django.core.validators import ValidationError, MinValueValidator, MaxValueValidator
from parking_req .models import ParkingUserModel


def katakana_only(value):
        if(re.match(r'^[ァ-ヶ]*$', value) == None):
            raise ValidationError(
                '%(value)s をカタカナで入力してください',\
                params={'value': value},
            )

class HostUserModel(models.Model):

    #id = models.IntegerField(default=0, verbose_name='オーナーID')
    user_id = models.IntegerField(default=0, verbose_name='ユーザID')
    day = models.DateField(verbose_name='登録日') 
    pay = models.CharField(max_length=32, verbose_name='支払方法') 
    bank_name = models.CharField(max_length=32, validators=[katakana_only], \
        verbose_name='銀行名')
    bank_code = models.IntegerField(default=0, verbose_name='支店コード')
    bank_account_number = models.CharField(max_length=64, verbose_name='口座番号')
    QR_id = models.CharField(max_length=128, verbose_name='口座番号')

    def __str__(self):
         return '<カーシェアオーナー:id' + str(self.id) + '>'  


class ParentCategory(models.Model):
    parent_category = models.CharField('メーカー', max_length=255)

    def __str__(self):
        return self.parent_category


class Category(models.Model):
    category = models.CharField('車種', max_length=255)
    parent_category = models.ForeignKey(ParentCategory, verbose_name='親カテゴリ', on_delete=models.PROTECT)

    def __str__(self):
        return self.category


class CarInfoModel(models.Model):
    # car_id = models.AutoField(primary_key=True) #車両ID
    user_id = models.IntegerField(default=0, verbose_name='ユーザID')
    day = models.DateField(verbose_name='登録日')
    parent_category = models.ForeignKey(ParentCategory, verbose_name='親カテゴリ', on_delete=models.PROTECT)
    category = models.ForeignKey(Category, verbose_name='車種', default=0, on_delete=models.PROTECT)
    license_plate = models.CharField(max_length=12, verbose_name='ナンバープレート')    	
    model_id = models.CharField(max_length=128, verbose_name='型番')
    custom = models.CharField(max_length=128, verbose_name='カスタム')	
    people = models.IntegerField(default=0, verbose_name='乗車人数')
    tire = models.CharField(max_length=128, verbose_name='タイヤ')
    used_years = models.IntegerField(default=0, verbose_name='使用年数(年単位)')
    vehicle_inspection_day = models.DateField(verbose_name='次回車検予定日')

    def __str__(self):
         return '<car_id=' + str(self.id) + '>'  


class CarInfoParkingModel(models.Model):
    user_id = models.IntegerField(default=0, verbose_name='ユーザID')
    car_id = models.ForeignKey(CarInfoModel, on_delete=models.CASCADE, verbose_name='車両ID')
    parking_id =  models.ForeignKey(ParkingUserModel, on_delete=models.CASCADE, verbose_name='駐車場ID')
    def __str__(self):
        return '<user_id=' +str(self.user_id) + str(self.car_id) + str(self.parking_id) + '>'

class CarsharingDateModel(models.Model):
    user_id = models.IntegerField(default=0, verbose_name='ユーザID')
    car_id = models.ForeignKey(CarInfoModel, on_delete=models.CASCADE, verbose_name='車両ID')
    possible_date = models.CharField(verbose_name='貸出可能日', max_length=10)

    def __str__(self):
      return '<date_id=' + str(self.user_id) + str(self.car_id) + self.possible_date + '>'