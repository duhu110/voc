# V2 Final 第三轮真实样本验证报告

- 模型：`Qwen3-Max`
- 样本数：`10`
- 一级命中：`7/10`
- 二级命中：`6/10`
- 叶子命中：`6/10`

## 样本结果

### WeComQH20240826150706758197

- 人工判断：`INSTALL_DELIVERY / INSTALL_TIMELINESS / 履约不及时/未履约`
- AI 判断：`INSTALL_DELIVERY / INSTALL_TIMELINESS / 履约不及时/未履约`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户已办理拆机并被承诺当天上门处理，但始终无人联系，主矛盾是履约未兑现。
- AI 理由：工单核心问题是用户已办理拆机销户业务，但运营商未按承诺时间上门或联系完成拆机，属于服务履约未兑现，应归入 INSTALL_DELIVERY / INSTALL_TIMELINESS 下的“履约不及时/未履约”。虽然涉及销户，但争议焦点不是销户规则或退订本身，而是履约过程未执行。

### WeComQH20240821175638346862

- 人工判断：`NETWORK_QUALITY / NETWORK_QUALITY / 宽带掉线/网络不稳定`
- AI 判断：`INSTALL_DELIVERY / INSTALL_STANDARD_AND_RESULT / 安装施工质量问题`
- 命中情况：一级=`False`，二级=`False`，叶子=`False`
- 人工理由：宽带昨天报修、今天再次无法连接，核心是网络恢复后仍不稳定，不是单纯装维时效问题。
- AI 理由：工单核心问题是宽带在维修后再次出现故障，属于修障不彻底，反映的是安装或维修施工的质量问题，应归入 INSTALL_DELIVERY / INSTALL_STANDARD_AND_RESULT / 安装施工质量问题。

### WeComQH20240821174529354782

- 人工判断：`PRODUCT_PLATFORM / QUERY_AND_DISPLAY / 网站/平台/客户端软件问题`
- AI 判断：`PRODUCT_PLATFORM / APP_AND_ACCOUNT / APP/网厅报错或线上办理失败`
- 命中情况：一级=`True`，二级=`False`，叶子=`False`
- 人工理由：用户在翼支付 APP 上领取会员权益失败，核心是客户端平台问题。
- AI 理由：工单核心问题是用户在使用翼支付APP时无法正常领取会员权益，属于APP功能异常或线上办理失败范畴，与费用、订购否认、网络质量等无关，最匹配的叶子分类为“APP/网厅报错或线上办理失败”。

### WeComQH20240810094622989578

- 人工判断：`FEE_BILLING / REFUND_PENALTY_RIGHTS / 翼支付权益/费用争议`
- AI 判断：`FEE_BILLING / REFUND_PENALTY_RIGHTS / 翼支付权益/费用争议`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：加油后权益金未返还，属于翼支付权益兑现和费用争议。
- AI 理由：工单核心问题是翼支付营销活动中承诺的权益金未到账，属于费用返还类争议，且可选分类中明确包含‘翼支付权益/费用争议’这一叶子节点，与工单内容高度匹配。

### WeComQH20240805160832347809

- 人工判断：`SERVICE_PROCESS / COMPLAINT_HANDLING / 处理结果不认可`
- AI 判断：`SERVICE_PROCESS / COMPLAINT_HANDLING / 处理结果不认可`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：回单声称已处理且用户认可，但用户明确表示未接到电话，主矛盾是对处理结果和回单内容不认可。
- AI 理由：工单核心在于用户对故障处理结果（系统记录“用户认可”）不认可，且否认曾被联系确认，属于对投诉处理结果的异议，应归入 SERVICE_PROCESS / COMPLAINT_HANDLING 下的“处理结果不认可”。虽然涉及装维服务，但问题焦点并非安装交付过程本身，而是对处理闭环真实性的质疑。

### WeComQH20240803151527459462

- 人工判断：`MARKETING_SALES / SALES_PROCESS_AND_ATTITUDE / 业务办理不畅`
- AI 判断：`SUBSCRIBE_CANCEL / PLAN_CHANGE_AND_ACCOUNT_CLOSE / 套餐变更争议`
- 命中情况：一级=`False`，二级=`False`，叶子=`False`
- 人工理由：用户要变更套餐但被 CRM 在途单卡住，核心是办理链路不畅。
- AI 理由：工单核心问题是用户要求变更套餐但因系统在途单受阻，属于套餐变更过程中的争议，符合SUBSCRIBE_CANCEL/PLAN_CHANGE_AND_ACCOUNT_CLOSE下的'套餐变更争议'分类。

### WeComQH20240724111625585117

- 人工判断：`OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / 复机/恢复失败或不及时`
- AI 判断：`OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / 复机/恢复失败或不及时`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户已做二次实名但仍迟迟未复机，核心是恢复不及时。
- AI 理由：工单核心问题是用户已完成涉诈停机后的复机手续（二次实名认证），但运营商未按承诺时间恢复服务，属于复机不及时问题，直接对应 OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK 下的‘复机/恢复失败或不及时’分类。

### WeComQH20240719101034109437

- 人工判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / 发票问题`
- AI 判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / 发票问题`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户要求核实并开具发票，主问题是开票金额和发票获取争议。
- AI 理由：工单核心是用户对发票开具金额存在疑问，属于账单发票类问题，且可选分类中明确包含‘发票问题’这一叶子节点，符合FEE_BILLING / ACCOUNT_AND_PAYMENT路径。

### WeComQH20240718105654266153

- 人工判断：`RULE_POLICY / USAGE_AND_LIMIT_RULE / 达量降速/限速规则争议`
- AI 判断：`FEE_BILLING / PACKAGE_AND_USAGE_FEE / 套外使用费用争议`
- 命中情况：一级=`False`，二级=`False`，叶子=`False`
- 人工理由：用户认为套餐应为达量降速不收费，但现行规则是超出流量继续收费，核心是达量降速规则争议。
- AI 理由：工单核心问题是用户对超出套餐流量后产生的收费不认可，属于套外使用费用的争议，而非套餐本身收费、订购否认或规则解释问题。尽管涉及达量降速规则，但争议焦点是已产生的套外费用，因此归入套外使用费用争议最准确。

### WeComQH20240713120226578278

- 人工判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / 用户否认订购`
- AI 判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / 用户否认订购`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户明确否认曾订购该合约业务，核心是对订购关系本身不认可。
- AI 理由：工单核心问题是用户明确否认曾订购某增值业务，符合‘用户否认订购’分类的定义，且该分类在V2体系中直接对应此场景。

## 失配观察

- `WeComQH20240821175638346862`: 人工=`宽带掉线/网络不稳定`，AI=`安装施工质量问题`
- `WeComQH20240821174529354782`: 人工=`网站/平台/客户端软件问题`，AI=`APP/网厅报错或线上办理失败`
- `WeComQH20240803151527459462`: 人工=`业务办理不畅`，AI=`套餐变更争议`
- `WeComQH20240718105654266153`: 人工=`达量降速/限速规则争议`，AI=`套外使用费用争议`
