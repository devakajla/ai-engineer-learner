# BMI category

Write `bmi_category(weight_kg, height_m)` that computes BMI (`weight / height ** 2`) and returns `"underweight"` (below 18.5), `"normal"` (below 25), `"overweight"` (below 30) or `"obese"` (30 or more).

```python
bmi_category(50, 1.8)    # -> "underweight"
bmi_category(70, 1.75)   # -> "normal"
bmi_category(95, 1.75)   # -> "obese"
```

**Think first:** what are the cut-off values? What happens exactly at 25?

**Hint:** compute `bmi` first, then early `return`s.
