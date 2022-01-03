#WT1
LTT_S = 1
LTT_V = 12

LFT_S = 1
LFT_V = 12

GC_S = 1
GC_V = 1

R = 1

WT1_real = (R + (LTT_S*LTT_V) + (LFT_S*LFT_V)) * (GC_S * GC_V) 
WT1_estimate = (LTT_S+LFT_S)*GC_S * (LTT_V+LFT_V+R)*GC_V
print(f"WT1 real: {WT1_real}  ,  WT1 estimate: {WT1_estimate}")




#WT2
LTT_S = 1
LTT_V = 13

LFT_S = 1
LFT_V = 13

GC_S = 1
GC_V = 1

R = 1

WT2_real = (R + (LTT_S*LTT_V) + (LFT_S*LFT_V)) * (GC_S * GC_V) 
WT2_estimate = (LTT_S+LFT_S)*GC_S * (LTT_V+LFT_V+R)*GC_V
print(f"WT1 real: {WT2_real}  ,  WT1 estimate: {WT2_estimate}")




#WT3
LTT_S = 1
LTT_V = 14

LFT_S = 1
LFT_V = 14

GC_S = 1
GC_V = 3

R = 1

WT3_real = (R + (LTT_S*LTT_V) + (LFT_S*LFT_V)) * (GC_S * GC_V) 
WT3_estimate = (LTT_S+LFT_S)*GC_S * (LTT_V+LFT_V+R)*GC_V
print(f"WT1 real: {WT3_real}  ,  WT1 estimate: {WT3_estimate}")




#Comparison
real_comparison = (WT1_real < WT2_real) and (WT2_real < WT3_real)
estimate_comparison = (WT1_estimate < WT2_estimate) and (WT2_estimate < WT3_estimate)

print(f"real comparison: {real_comparison}  ,  estimate comparison: {estimate_comparison}")