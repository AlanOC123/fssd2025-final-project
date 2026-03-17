import { GooeyToaster as GoeyToasterPrimitive, gooeyToast } from "goey-toast"
import type { GooeyToasterProps } from "goey-toast"
import "goey-toast/styles.css"

export { gooeyToast }
export type { GooeyToasterProps }
export type {
  GooeyToastOptions,
  GooeyPromiseData,
  GooeyToastAction,
  GooeyToastClassNames,
  GooeyToastTimings,
} from "goey-toast"

function GoeyToaster(props: GooeyToasterProps) {
  return <GoeyToasterPrimitive position="bottom-right" {...props} />
}

export { GoeyToaster }
