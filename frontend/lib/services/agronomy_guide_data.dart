class AgronomyGuideSection {
  final String titleEn;
  final String titleUr;
  final String contentEn;
  final String contentUr;

  const AgronomyGuideSection({
    required this.titleEn,
    required this.titleUr,
    required this.contentEn,
    required this.contentUr,
  });
}

const List<AgronomyGuideSection> agronomyGuideData = [
  AgronomyGuideSection(
    titleEn: "1. Soil Preparation & Fertilization",
    titleUr: "1۔ زمین کی تیاری اور کھاد کی مقدار",
    contentEn: "• Wheat: Plough field 2-3 times. Apply 1 bag DAP + 1/2 bag Urea at sowing.\n"
        "• Rice: Puddle the soil before transplanting. Apply 1 bag DAP + 1 bag Urea.\n"
        "• Cotton: Deep ploughing to break hardpan. Apply 1.5 bag DAP + 1 bag Potassium Sulfate at sowing.\n"
        "• Maize: Create fine seedbed. Apply 1.5 bag DAP + 1 bag Urea during sowing.",
    contentUr: "• گندم: زمین کو 2 سے 3 بار ہل چلائیں۔ بوائی کے وقت 1 بوری DAP اور آدھی بوری یوریا ڈالیں۔\n"
        "• چاول: منتقلی سے پہلے زمین کو کدو کریں۔ 1 بوری DAP اور 1 بوری یوریا استعمال کریں۔\n"
        "• کپاس: گہرا ہل چلائیں۔ بوائی پر ڈیڑھ بوری DAP اور 1 بوری پوٹاشیم سلفیٹ ڈالیں۔\n"
        "• مکئی: نرم مٹی تیار کریں۔ بوائی پر ڈیڑھ بوری DAP اور 1 بوری یوریا استعمال کریں۔",
  ),
  AgronomyGuideSection(
    titleEn: "2. Irrigation Timing & Water Needs",
    titleUr: "2۔ آبپاشی کا وقت اور پانی کی ضرورت",
    contentEn: "• Wheat: Requires 4-5 irrigations. Critical stages: Crown Root Initiation (21 days), Booting (80 days), Grain filling (110 days).\n"
        "• Rice: Maintain 2-3 inches of standing water during first 40 days, then alternate wet and dry cycles.\n"
        "• Cotton: 5-6 irrigations. Keep soil moist but avoid waterlogging. First irrigation at 35 days post sowing.\n"
        "• Maize: 8-10 irrigations. Critical stages: Tasseling, Silking, and Grain formation.",
    contentUr: "• گندم: 4 سے 5 پانی درکار ہیں۔ اہم مراحل: تاج جڑ نکلنا (21 دن)، بوٹنگ (80 دن)، دانہ بھرنا (110 دن)۔\n"
        "• چاول: پہلے 40 دنوں کے دوران 2 سے 3 انچ پانی کھڑا رکھیں، پھر باری باری خشک اور گیلا کرنے کا سائیکل چلائیں۔\n"
        "• کپاس: 5 سے 6 پانی۔ مٹی کو نم رکھیں لیکن پانی کھڑا نہ ہونے دیں۔ پہلا پانی بوائی کے 35 دن بعد۔\n"
        "• مکئی: 8 سے 10 پانی۔ اہم مراحل: ٹیسلنگ، سلکنگ، اور دانہ بننا۔",
  ),
  AgronomyGuideSection(
    titleEn: "3. Pest & Disease Quick Reference",
    titleUr: "3۔ عام بیماریوں کی علامات اور علاج",
    contentEn: "1. Aphids: Sucking pests. Symptoms: Yellow leaves. Control: Spray Imidacloprid.\n"
        "2. Whitefly: Sucking pest. Symptoms: Sticky leaves, soot. Control: Spray Acetamiprid.\n"
        "3. Pink Bollworm: Symptoms: Damaged bolls, lint staining. Control: Pheromone traps, Triazophos.\n"
        "4. Stem Borer (Rice): Symptoms: Dead hearts. Control: Apply Carbofuran granules.\n"
        "5. LeafFolder: Symptoms: Folded leaves. Control: Spray Cartap Hydrochloride.\n"
        "6. Armyworm: Symptoms: Eaten foliage. Control: Spray Emamectin Benzoate.\n"
        "7. Rust (Wheat): Symptoms: Yellow/brown pustules on leaves. Control: Spray Propiconazole.\n"
        "8. Late Blight (Potato): Symptoms: Water-soaked spots on leaves. Control: Metalaxyl + Mancozeb.\n"
        "9. Fruit Borer (Tomato): Symptoms: Holes in fruits. Control: Chlorantraniliprole.\n"
        "10. Thrips: Symptoms: Silvery leaves. Control: Spray Spinetoram.",
    contentUr: "1۔ تیلا (Aphids): پتے پیلے ہونا۔ علاج: امیڈا کلوپرڈ سپرے کریں۔\n"
        "2۔ سفید مکھی: پتے چپچپا ہونا اور کالا ہونا۔ علاج: ایسیٹامپرڈ سپرے کریں۔\n"
        "3۔ گلابی سنڈیں: ٹینڈے کا نقصان۔ علاج: فیرومون ٹریپ اور ٹرائیازوفاس۔\n"
        "4۔ تنے کی سنڈیں (چاول): تنے کا خشک ہونا۔ علاج: کاربوفوران دانے دار کھاد۔\n"
        "5۔ پتا لپیٹ سنڈی: لپٹے ہوئے پتے۔ علاج: کارٹاپ ہائیڈروکلورائڈ سپرے کریں۔\n"
        "6۔ لشکر سنڈی: پتے کھائے جانا۔ علاج: ایما میکٹن بینزوئیٹ سپرے کریں۔\n"
        "7۔ کُنگ (گندم): پیلے اور بھورے دھبے۔ علاج: پروپیکونازول سپرے کریں۔\n"
        "8۔ جھلسائو (آلو): پتوں پر کالے دھبے۔ علاج: میٹالیکسیل + مینکوزیب سپرے۔\n"
        "9۔ پھل کی سنڈی (ٹماٹر): پھل میں سوراخ۔ علاج: کلورینٹرانیلی پرول سپرے کریں۔\n"
        "10۔ تھرپس: چمکدار پتے۔ علاج: اسپنیشورم سپرے۔",
  ),
  AgronomyGuideSection(
    titleEn: "4. Seasonal Crop Calendar",
    titleUr: "4۔ علاقائی فصلی تقویم",
    contentEn: "• Punjab: Rabi Sowing (Oct-Dec), Kharif Sowing (Apr-Jun). Cotton sowing starts mid-May.\n"
        "• Sindh: Sowing starts 1 month earlier than Punjab due to warmer climate. Cotton sowing in March.\n"
        "• KPK: Sowing depends on altitude. Temperate valleys sow maize in April and wheat in November.",
    contentUr: "• پنجاب: ربیع کی کاشت (اکتوبر-دسمبر)، خریف کی کاشت (اپریل-جون)۔ کپاس مئی کے وسط میں۔\n"
        "• سندھ: درجہ حرارت زیادہ ہونے کی وجہ سے کاشت پنجاب سے ایک ماہ پہلے ہوتی ہے۔ کپاس مارچ میں۔\n"
        "• کے پی کے: اونچائی پر منحصر ہے۔ معتدل وادیوں میں مکئی اپریل اور گندم نومبر میں کاشت کی جاتی ہے۔",
  ),
  AgronomyGuideSection(
    titleEn: "5. Safe Pesticide Usage & Dosage",
    titleUr: "5۔ کیڑے مار ادویات کی خوراک اور احتیاط",
    contentEn: "• Imidacloprid 20% SL: 250ml per acre in 100L water. Target: Whitefly/Aphids.\n"
        "• Emamectin Benzoate 1.9% EC: 200ml per acre. Target: Bollworms.\n"
        "• Propiconazole 25% EC: 200ml per acre. Target: Rust.\n"
        "• Glyphosate 41% SL: 1 Liter per acre. Target: Weeds.\n"
        "• Safety: Always wear gloves, masks, and spray in direction of wind. Keep out of reach of children.",
    contentUr: "• امیڈا کلوپرڈ 20%: 250 ملی لیٹر فی ایکڑ، 100 لیٹر پانی میں۔ حدف: سفید مکھی۔\n"
        "• ایما میکٹن بینزوئیٹ 1.9%: 200 ملی لیٹر فی ایکڑ۔ حدف: گلابی سنڈی۔\n"
        "• پروپیکونازول 25%: 200 ملی لیٹر فی ایکڑ۔ حدف: کُنگ۔\n"
        "• گلائفوسیٹ 41%: 1 لیٹر فی ایکڑ۔ حدف: جڑی بوٹیاں۔\n"
        "• حفاظتی تدابیر: ہمیشہ دستانے اور ماسک پہنیں، اور ہوا کے رخ پر سپرے کریں۔ بچوں سے دور رکھیں۔",
  ),
  AgronomyGuideSection(
    titleEn: "6. Post-Harvest Storage Tips",
    titleUr: "6۔ کٹائی کے بعد ذخیرہ اندوزی",
    contentEn: "1. Dry grains below 12% moisture level to prevent fungal growth.\n"
        "2. Clean and fumigate storage rooms with Aluminium Phosphide tablets.\n"
        "3. Keep storage bags on elevated wooden planks away from walls to prevent moisture seepage.\n"
        "4. Ensure proper ventilation but seal rooms against rodents.",
    contentUr: "1۔ اناج کو 12 فیصد سے کم نمی کی سطح تک خشک کریں تاکہ فنگس نہ لگے۔\n"
        "2۔ گودام کی صفائی کریں اور ایلومینیم فاسفائیڈ کی گولیاں رکھ کر دھواں دیں۔\n"
        "3۔ بوریوں کو لکڑی کے تختوں پر رکھیں اور دیواروں سے دور رکھیں تاکہ نمی سے بچ سکیں۔\n"
        "4۔ مناسب ہوا کا گزر یقینی بنائیں لیکن چوہوں کے داخلے کے راستے بند کریں۔",
  ),
];
