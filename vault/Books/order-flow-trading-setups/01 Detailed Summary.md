---
doc_id: "3605e0c990fe"
book_title: "Order Flow Trading Setups"
author: "Trader Dale"
file_path: "books/Order-Flow-Trading-Setups-1.pdf"
page_start: 1
page_end: 161
---

# Detailed Summary

*Order Flow Trading Setups by Trader Dale*

## Introduction and scope

Dale starts from a practical problem: after identifying price areas with a profile, he wanted to see how trading was actually distributed when the market reached them. He describes moving from watching the depth-of-market ladder to a footprint that keeps a record inside each price bar. The figures and prescriptions that follow are educational examples. The disclosure identifies the book's trade examples as hypothetical, which matters when distinguishing a pattern illustration from evidence of repeatable results.

[PDF pp. 1–13](../../../books/Order-Flow-Trading-Setups-1.pdf#page=1)

## Workspace and data selection

The trading workflow depends on access to granular, executed size. The author covers a particular platform and futures feed, then explains why a centralized futures contract is a stronger basis for a bid-by-ask footprint than a single spot FX feed. If analysis and execution use different instruments, establish the price correspondence first. The inverse currency example is valuable because directional resemblance does not make levels or minimum tick increments interchangeable.

[PDF pp. 14–19](../../../books/Order-Flow-Trading-Setups-1.pdf#page=14)

- **Footprints Need Venue-Level Executed Volume**. Centralized futures data lets the analyst observe executed size by price and side for that contract. Spot FX is decentralized, so a feed from one broker gives only a partial view of spot activity. Dale uses currency futures for analysis and maps the levels separately when executing in spot. (pp. 17–19)
- **Map Currency Futures Levels Before Spot Execution**. Currency futures and spot pairs can use different quotation directions and price scales. Dale compares them side-by-side and uses an inverse display where appropriate. A corresponding swing or zone must be mapped to the execution instrument. (pp. 19–20)

## Aggressive and passive participants

Read each print as a matched trade. A market buy taking the ask has a resting seller on the other side. A market sell hitting the bid has a resting buyer on the other side. A large print therefore answers where and how much traded and which side initiated. The passive side's importance comes into view when the aggressive push fails to move price. Inference about an institution taking or defending inventory requires more evidence than the print alone.

[PDF pp. 20–24](../../../books/Order-Flow-Trading-Setups-1.pdf#page=20)

- **Aggressive and Passive Orders Share Each Print**. A market buy executes against a resting sell limit at the ask. A market sell executes against a resting buy limit at the bid. The print locates the transaction and its aggressive side, while the price response helps infer whether the passive side mattered. (pp. 20–24)
- **You Cannot Identify the Trader From the Print**. A conspicuous ask-side execution could reflect buying initiative or the ability of a passive seller to absorb it. The number identifies the traded size, and the price response supplies separate information. Dale treats participant identity and intent as inferences. (pp. 24–25)

## Footprints delta and daily profile

A footprint adds rows of executions to a normal candle. Dale's highest-volume row combines bid and ask at that price, while bar delta subtracts all bid executions from all ask executions. Candle direction and delta can agree during a clear trend or diverge around a contested level. His daily profile provides the longer view of volume at price. It is useful to keep the local bar node, full-session concentration, and direction of aggression separate during a replay.

[PDF pp. 25–32](../../../books/Order-Flow-Trading-Setups-1.pdf#page=25)

- **The Footprint Shows Executions at Each Price**. A footprint keeps the candle's price range and layers executed bid and ask quantity onto each price row. This reveals where within the bar activity was concentrated. A normal candle only shows the aggregate price movement. (pp. 25–26)
- **A Footprint Node Is Its Busiest Price Row**. Dale defines a bar's high-volume node by the largest combined bid and ask volume at a single price. This is a local, per-bar reference. A different time window can produce a different node. (pp. 26–27)
- **Bar Delta Is Executed Ask Minus Bid**. Bar delta sums ask-side volume and subtracts bid-side volume across the footprint. A positive value indicates more buy-initiated execution, though the candle can still close lower. Rotations can make the relationship between delta and candle direction less reliable. (pp. 27–30)
- **Delta Can Diverge From Candle Direction**. An up bar with negative delta or a down bar with positive delta shows price and executed aggression are telling different stories. Dale uses this discrepancy to investigate a reaction near a planned level. The example pairs an advancing price with weaker delta at resistance. (pp. 28–30)
- **Daily Profile Adds Context to a Footprint**. Dale displays the day's volume distribution beside individual footprints to see where repeated trading took place. The daily histogram summarizes the session by price while the footprint shows how that activity was distributed within particular bars. (pp. 31–32)

## Clusters nodes imbalances and auction extremes

Darker total-volume rows make concentrations easier to locate. A repeated node relates the highest-volume prices across successive footprints and can be seen at a much narrower scale than a session profile. Diagonal imbalance compares opposite-side volume one price level away, while a stack groups multiple adjacent imbalances on one side. Unfinished business uses the footprint print at an extreme. Cumulative delta instead follows the running total of signed execution on another time axis. The workspace brings all of these into view, with separate charts for slower setup context and faster confirmation.

[PDF pp. 33–45](../../../books/Order-Flow-Trading-Setups-1.pdf#page=33)

- **Relative Volume Defines a Cluster**. Dale's footprint shades rows based on executed size so unusually heavy areas stand out from nearby prices. A cluster is a band of relatively heavy trading. Interpretation depends on where the cluster forms and how price subsequently leaves it. (pp. 34–35)
- **Multiple Nodes Share One Price Across Bars**. A double or triple node forms when the maximum-volume row repeats at the same price in successive footprints. A coincident level in separated bars is a different measurement. Dale treats this repetition as an area to watch when price returns. (pp. 35–36)
- **Footprint Imbalance Uses a Diagonal Comparison**. Dale's default imbalance compares executions on one side with the opposing volume at the neighboring price and highlights ratios of 3 to 1 or higher. The diagonal convention differs from whether one side is larger within a single row. The software ratio is configurable. (pp. 36–37)
- **A Stack Groups Neighboring Same-Side Imbalances**. Adjacent imbalance levels on the same side form a stack. Dale describes the usual display as three or more, while the trading instructions allow the configured trigger to vary. The stack highlights a band of unusually one-sided execution. (pp. 37–38)
- **Unfinished Business Is a Footprint-Extreme Test**. Dale expects zero executed bid volume at a finished footprint high and zero executed ask volume at a finished low. He marks an extreme with prints on both sides as unfinished business. The mark is a level to track, and revisits can take time or fail to occur. (pp. 38–41)
- **Cumulative Delta Adds Signed Execution Over Time**. Cumulative delta runs a sum of bar delta from the session start. Price and the running flow total can be shown on matching time axes to compare their direction. A different session reset changes the displayed series. (pp. 41–43)
- **Use Separate Views for Context and Confirmation**. Dale's workspace pairs slower footprints for setup location with a faster footprint and a separate cumulative-delta view. The session profile gives a broader map for the same market. Each panel answers a different question about location or timing. (pp. 44–45)

## Setup one volume clusters

A trend cluster is a relative bulge in volume within a clear directional leg. A rejection cluster forms within a sharp two-way event instead. In both cases the book first looks for separation from the band, then a later return to it. A trend uses the leg's direction, while the rejection setup uses the direction away from the rejected extreme. The examples include both long and short cases. Dale interprets the reaction as possible defense of earlier inventory reinforced by opposing traders reducing exposure. The participant story goes beyond what volume alone shows.

[PDF pp. 46–54](../../../books/Order-Flow-Trading-Setups-1.pdf#page=46)

- **Retest a Footprint Cluster Inside a Trend**. Find relatively heavy trading inside a decisive directional leg, then observe whether price separates from the band. Dale waits for a pullback to its initial boundary or heavier portion. He aligns the setup with the direction of the leg. (pp. 46–50)
- **Defending Inventory Can Explain a Cluster Retest**. Dale offers two explanations for a reaction at a prior cluster: earlier participants may defend their positions, and opposing traders may close as price approaches. Both are explanations for the observed reaction. The chart directly shows concentration, departure, return, and response. (pp. 47–48)
- **Profile the Cluster Inside a Sharp Rejection**. Look for a fast move that reverses decisively, then locate relatively heavy trading inside the rejection. Track the band after price clearly leaves it and test the first return in the direction of rejection. The move can span more than one candle. (pp. 51–54)

## Setup two multiple nodes

Two or more successive footprints share their highest-volume price in the multiple-node setup. The location must arise before or within a trend or inside a strong rejection. Dale waits for two entire footprints clear of the level and then considers its first test. This makes the setup different from simply counting how often a popular price traded. The time at which the two separating footprints finish and the direction of the return would be necessary measurements in a test.

[PDF pp. 55–59](../../../books/Order-Flow-Trading-Setups-1.pdf#page=55)

- **Require Separation Before a Multiple-Node Retest**. Dale looks for at least two consecutive bar nodes at the same price in a trend, pre-trend region, or strong rejection. His setup then waits for two entire footprints to form away from the node and considers its first later revisit. The approach determines the proposed side. (pp. 55–59)

## Setup three filtered trades

The trade-size filter reduces the visual density of the footprint to selected large executions. The book mostly uses slower footprints to mark those levels, requires price to move away, then watches the first retest. The lot threshold is instrument-specific. Split execution or an iceberg can make meaningful activity disappear from the filtered view, while a large visible print can have several explanations. The raw footprint is still useful to review before adopting a filter.

[PDF pp. 60–64](../../../books/Order-Flow-Trading-Setups-1.pdf#page=60)

- **A Large-Trade Filter Misses Split Execution**. The filter highlights single executions above a configurable size. Dale's 25-lot illustration is calibrated to his currency-futures example, and activity varies by instrument and session. Small clips and iceberg replenishment can be missed by a large-print cutoff. (pp. 60–61)
- **Track Retests of Filtered Large Execution Areas**. Identify a large execution with the trades filter, then wait for one or two entire footprints to build outside the marked area. Measure the first pullback to the zone after that separation. Dale uses the approach direction to distinguish support from resistance. (pp. 60–64)

## Setup four stacked imbalances

Dale uses a diagonal ratio to identify imbalance rows, then marks an adjacent same-side band as a potential reference. He looks for stacks within or ahead of a decisive one-way move and waits for a return after separation. The tested side is inferred from how price approaches the band. The examples illustrate a first-touch premise. A written replay rule should define the stack length, denominator treatment, intervening price movement and what counts as the first visit.

[PDF pp. 65–70](../../../books/Order-Flow-Trading-Setups-1.pdf#page=65)

- **Trade Stacked Imbalance Retests With Directional Context**. A stack during a one-way move defines a candidate band. Dale waits for price to move away before it comes back and uses only the first test in this setup. A buying stack approached from above is considered possible support, and the mirrored case possible resistance. (pp. 65–70)

## Setup five unfinished business

The author's footprint definition marks an extreme when both sides still have executed volume at the high or low. He treats it as a possible revisit reference and considers it when planning targets, stops, or confirmation. The nearby level can be useful in a planned trade. Some examples show a substantial interval before price returns, which prevents the mere existence of the feature from resolving entry timing.

[PDF pp. 71–79](../../../books/Order-Flow-Trading-Setups-1.pdf#page=71)

- **Treat Unfinished Business as a Nearby Reference**. Dale uses an unfinished extreme in target planning, stop placement, and trade screening. Its presence can support a revisit hypothesis when price is already near it, but the market may first move far away. The reference alone gives no dependable entry timing. (pp. 71–74)
- **Check Unfinished Extremes Before Placing Stops**. Dale checks whether a nearby unfinished extreme lies just beyond a proposed protective stop. The point is to understand whether a test of that extreme would also invalidate the chosen positioning. It remains secondary to the main setup and risk distance. (pp. 73–79)

## Confirmations at support and resistance

The chapter begins with a location already chosen. Large passive interest can be inferred when conspicuous volume appears but the extreme stops advancing. Dale's absorption examples emphasize unusually heavy two-sided activity around the stall. A complementary confirmation is aggressive execution away from the level, with the expected sign of delta. The examples that combine the first two concepts present passive interest stopping the prior move and aggressive interest supporting the next move. Their order and the time at which the evidence is visible matter.

[PDF pp. 80–98](../../../books/Order-Flow-Trading-Setups-1.pdf#page=80)

- **Choose a Reference Before Reading Confirmation**. Dale first identifies support or resistance with a primary method, then looks at order flow when price arrives. The four confirmation families are large passive orders, absorption, aggressive orders with delta, and cumulative-delta divergence. His presented confirmation setups depend on the location. (pp. 80–81)
- **Infer Passive Interest From a Stalled Extreme**. At resistance a large ask print can accompany aggressive buying into a passive seller while price fails to extend. At support the mirrored example shows large bid volume during a stalled sell push. Unusually large is relative to the instrument and the session. (pp. 81–86)
- **Watch Heavy Two-Sided Volume Where Price Stalls**. Dale's absorption setup looks for unusually heavy traded volume on both bid and ask around preselected support or resistance, while the previous push stalls. The evidence may take several minutes to appear. It is strongest as a response to a level already identified. (pp. 87–91)
- **Look for Aggression Away From the Reference**. Dale watches for dominant bid-side execution and negative delta at resistance, or dominant ask-side execution and positive delta at support. He reads the response within five-minute footprints in these examples. The proposed aggression is in the direction of the reaction away from the level. (pp. 92–95)
- **Absorption and Initiative Form Different Stages**. Dale describes a sequence in which passive interest first stalls a move and later aggressive traders push price away. The second stage supplies directional follow-through beyond the first stall. The footprint examples mark both stages separately. (pp. 95–98)

## Cumulative-delta divergence

Dale compares price and cumulative delta around strong support and resistance. His long formulation shows price drifting lower while cumulative delta climbs, with the mirror setup applying on the short side. The series align at the same times. The book's price-following-flow interpretation is one possible resolution. It is worth recording the actual price response and whether the level held rather than inferring the outcome from divergence alone.

[PDF pp. 99–104](../../../books/Order-Flow-Trading-Setups-1.pdf#page=99)

- **Read Cumulative-Delta Divergence Around Planned Levels**. Dale's long example compares falling price with rising cumulative delta near support, with the mirror case near resistance. The mismatch is evaluated where the primary strategy already identified a meaningful zone. The hoped-for resolution belongs to the chart example and needs its own outcome test. (pp. 99–104)

## Targets and trailing

Earlier heavy-volume bands provide candidate target areas because the move can slow when it reaches another accepted price range. Dale discusses using the near side rather than requiring price to traverse the whole band. His trailing method follows favorable aggression, while opposing imbalances, absorption or a delta change at a significant location can alter the assessment. The logic connects the target and exit to price location and real-time movement rather than a single color change.

[PDF pp. 105–114](../../../books/Order-Flow-Trading-Setups-1.pdf#page=105)

- **Aim at the Near Edge of Prior Volume**. When a trade approaches a zone with heavy historical activity, Dale considers taking profit before or at its leading edge. The zone may interrupt the move. A target selected from that distribution inherits the profile's window and price bins. (pp. 105–109)
- **Reassess a Trail When Order Flow Turns**. Dale trails a favorable position while aggressive execution still supports the move. Opposing imbalance, renewed absorption, or a delta reversal near a significant price can change that read. The decision is conditioned on price location and progress. (pp. 110–114)

## Stops and structural invalidation

Dale compares keeping a fixed stop with placing it beyond the relevant high or low or behind a heavy-volume band. The structural choices express the price at which the trade premise fails. He also checks the distance relative to normal activity in the market. The stop examples show a physical separation between the proposed support line and the protective stop. The example ranges are instrument illustrations.

[PDF pp. 115–120](../../../books/Order-Flow-Trading-Setups-1.pdf#page=115)

- **Place Stops Beyond the Price Structure**. The book compares a fixed stop, a stop beyond the support or resistance extreme, and a stop beyond a heavy-volume band. The structural approaches tie the stop to the trade premise. Dale checks whether the resulting distance is sensible for the instrument and market conditions. (pp. 115–120)

## Reading the volume profile

The profile displays total executed volume at each price, unlike bars that total volume by time. A D profile summarizes a balanced central concentration. A P profile has volume concentrated above its stem, a lowercase b below its thinner portion, and a thin profile can reflect a fast one-way move. These are descriptions of a selected window. Dominant and thin regions give areas to watch when examining the next auction.

[PDF pp. 121–129](../../../books/Order-Flow-Trading-Setups-1.pdf#page=121)

- **Volume Profile Plots Executed Size by Price**. A horizontal histogram bins executions by price across a selected interval. The thick portions show where more traded, whereas ordinary volume bars total activity by time interval. The profile identifies candidate price zones for further assessment. (pp. 121–124)
- **Profile Shape Describes Where Business Concentrated**. Dale associates D with a broad middle distribution, P with a higher bulge, lowercase b with a lower bulge, and thin profiles with directional travel. Each shape summarizes where volume accumulated. The time window affects which shape is visible. (pp. 125–128)

## Three flexible volume-profile setups

For accumulation, isolate the rotation before the directional departure and mark its heaviest price band. For trend, isolate the impulse and identify the volume bump inside it. For rejection, include the rejected probe and reversal and locate the busy area inside that exchange. Each gives a prospective reference for a return, then the chapter brings the faster order-flow confirmation back into the sequence. The rejection setup is harder to apply when several bands compete for the reference.

[PDF pp. 130–145](../../../books/Order-Flow-Trading-Setups-1.pdf#page=130)

- **Profile the Rotation Before a Directional Departure**. Dale profiles the pre-move range and highlights its heaviest traded band once price breaks out. A later return to that band becomes a support or resistance candidate. The book pairs the return with a separate order-flow confirmation. (pp. 130–136)
- **Profile a Pause Within an Established Trend**. A strong directional move can leave a thin distribution with a relatively large bump where it paused. Dale focuses on that local concentration for a potential continuation retest. The underlying trend and the actual response at the band are both part of his setup. (pp. 137–140)
- **Profile the Whole Rejection to Find the Fight**. Apply a flexible profile over a strong rejected probe and its reversal to find the heaviest traded band inside the event. This can expose levels hidden by different candle time frames. Dale describes the method as harder to apply when several concentrations compete. (pp. 141–145)

## Closing material

The book closes with advice to practice the methods and with product information, testimonials, and publication material. The analytical chapters make the distinction between identifying candidate locations and using order flow to read the response. For study, a repeated replay exercise across trend, rejection, and rotation can show which pieces are observable and which are interpretations.

[PDF pp. 146–161](../../../books/Order-Flow-Trading-Setups-1.pdf#page=146)
