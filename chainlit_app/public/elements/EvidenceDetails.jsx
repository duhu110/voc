import { AlertTriangle, FileSearch, History, Layers3, Tags } from "lucide-react";

export default function EvidenceDetails() {
  const ticket = props.ticket || {};
  const classification = props.classification || {};
  const riskNotes = props.riskNotes || [];
  const replyStandards = props.replyStandards || [];
  const matchedAdvices = props.matchedAdvices || [];
  const summarySamples = props.summarySamples || [];
  const fields = [
    ["主分类", classification.primary],
    ["产品标签", classification.product],
    ["诉求标签", classification.request],
    ["风险标签", classification.risk],
    ["情绪标签", classification.emotion],
  ];

  return (
    <div className="voc-evidence mt-3 text-sm">
      <div className="voc-evidence__summary flex items-center justify-between gap-3 px-4 py-3 font-medium">
        <span className="flex min-w-0 items-center gap-2">
          <FileSearch className="h-4 w-4 shrink-0 text-primary" />
          <span className="truncate">附加信息</span>
        </span>
        <span className="shrink-0 text-xs text-muted-foreground">{matchedAdvices.length} 条依据</span>
      </div>

      <div className="space-y-4 border-t border-border px-4 py-3">
          <section>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <FileSearch className="h-4 w-4 text-primary" />
              工单理解
            </h3>
            <div className="space-y-1 text-muted-foreground">
              <div>临时工单号：{ticket.ticketId || "-"}</div>
              <div>投诉现象：{ticket.complaintPhenomenon || "-"}</div>
              <div>投诉内容：{ticket.bizContent || "-"}</div>
              <div>线路分类：{ticket.lineCategory || "未提供"}</div>
            </div>
          </section>

          <section>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <Tags className="h-4 w-4 text-primary" />
              分类与标签
            </h3>
            <div className="grid gap-2 sm:grid-cols-2">
              {fields.map(([label, value]) => (
                <div key={label} className="voc-evidence__item rounded-md border border-border/70 p-2">
                  <div className="text-xs text-muted-foreground">{label}</div>
                  <div className="mt-1 font-medium">{value?.name || "-"}</div>
                  <div className="text-xs text-muted-foreground">{value?.code || "-"}</div>
                </div>
              ))}
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              置信度：{classification.confidence || "-"} · 需要人工复核：
              {classification.needsHumanReview ? "是" : "否"}
            </div>
          </section>

          <section>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <AlertTriangle className="h-4 w-4 text-primary" />
              风险提醒
            </h3>
            {riskNotes.length ? (
              <div className="voc-evidence__item rounded-md border border-border/70 p-3">
                <div className="space-y-1">
                  {riskNotes.map((note, index) => (
                    <div key={index}>{note}</div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="voc-evidence__item rounded-md border border-border/70 p-3 text-muted-foreground">
                未发现额外风险提醒。
              </div>
            )}
          </section>

          <section>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <FileSearch className="h-4 w-4 text-primary" />
              回单规范提醒
            </h3>
            {replyStandards.length ? (
              <div className="space-y-2">
                {replyStandards.map((item, index) => (
                  <div key={item.title || index} className="voc-evidence__item rounded-md border border-border/70 p-3">
                    <div className="font-medium">{item.title || "-"}</div>
                    <div className="mt-1 text-muted-foreground">{item.content || "-"}</div>
                    {item.applicability_note ? (
                      <div className="mt-2 text-xs text-muted-foreground">
                        适用条件：{item.applicability_note}
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">暂无额外回单规范提醒。</p>
            )}
          </section>

          <section>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <Layers3 className="h-4 w-4 text-primary" />
              命中依据
            </h3>
            {matchedAdvices.length ? (
              <div className="space-y-2">
                {matchedAdvices.map((advice, index) => (
                  <div key={advice.id || index} className="voc-evidence__item rounded-md border border-border/70 p-3">
                    <div className="font-medium">{advice.advice_title || "-"}</div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <span className="voc-chip">命中级别：{advice.match_level || "-"}</span>
                      <span className="voc-chip">样本数：{advice.source_summary_count ?? "-"}</span>
                      <span className="voc-chip">来源工单：{advice.latest_source_ticket_id || "-"}</span>
                    </div>
                    {advice.applicability_note ? (
                      <div className="mt-2 text-xs text-muted-foreground">
                        适用条件：{advice.applicability_note}
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">未命中建议。</p>
            )}
          </section>

          <section>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <History className="h-4 w-4 text-primary" />
              历史摘要样本
            </h3>
            {summarySamples.length ? (
              <div className="space-y-2">
                {summarySamples.slice(0, 5).map((sample, index) => (
                  <div key={sample.source_ticket_id || index} className="voc-evidence__item rounded-md border border-border/70 p-3">
                    <div className="text-xs font-medium text-muted-foreground">
                      {sample.source_ticket_id || "-"}
                    </div>
                    <div className="mt-1">{sample.resolution_summary || "-"}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">暂无历史摘要样本。</p>
            )}
          </section>
      </div>
    </div>
  );
}
