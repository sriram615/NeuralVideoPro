"use client";

interface PipelineStep {
  step: number;
  title: string;
  desc: string;
}

interface PipelineStepsProps {
  steps: PipelineStep[];
  activeStep: number;
}

export default function PipelineSteps({ steps, activeStep }: PipelineStepsProps) {
  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-black/90 border border-accent-cyan/50 rounded-2xl backdrop-blur-2xl shadow-2xl space-y-4 animate-fade-in" aria-label="Pipeline progress">
      <div className="flex items-center justify-between border-b border-white/10 pb-3 font-mono">
        <div className="flex items-center gap-3">
          <div className="w-4 h-4 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" aria-hidden="true" />
          <span className="font-bold text-xs text-accent-cyan/80 tracking-wider uppercase">
            LIVE PIPELINE STORYTELLING VISUALIZATION
          </span>
        </div>
        <span className="text-xs text-gray-400">STEP {activeStep} OF {steps.length}</span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-left font-mono">
        {steps.map((item) => {
          const isDone = activeStep > item.step;
          const isActiveStep = activeStep === item.step;

          return (
            <div
              key={item.step}
              className={`p-3 rounded-xl border transition-all duration-200 ${
                isDone
                  ? "bg-accent-emerald/60 border-accent-emerald/50 text-accent-emerald/80"
                  : isActiveStep
                  ? "bg-accent-cyan/80 border-accent-cyan text-accent-cyan shadow-[0_0_15px_rgba(6,182,212,0.3)]"
                  : "bg-white/5 border-white/10 text-gray-500"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-bold tracking-widest uppercase">
                  STEP {item.step}
                </span>
                <span aria-hidden="true">
                  {isDone ? (
                    <span className="text-accent-emerald font-bold">&check;</span>
                  ) : isActiveStep ? (
                    <span className="w-2 h-2 rounded-full bg-accent-cyan inline-block" />
                  ) : (
                    <span className="text-gray-600">&bull;</span>
                  )}
                </span>
              </div>
              <div className="font-bold text-xs truncate">{item.title}</div>
              <div className="text-[10px] text-gray-400 truncate">{item.desc}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
