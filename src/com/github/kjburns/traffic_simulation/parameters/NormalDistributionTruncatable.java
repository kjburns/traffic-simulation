package com.github.kjburns.traffic_simulation.parameters;

import java.util.UUID;

import org.apache.commons.math3.distribution.NormalDistribution;
import org.w3c.dom.Element;

/**
 * An optionally-truncatable normal distribution.
 * @author Kevin J. Burns
 *
 */
class NormalDistributionTruncatable extends AbstractDistribution<Double> {
	public static class Factory {
		public static class Options {
			private boolean reverse = false;
			private double minValue = Double.NEGATIVE_INFINITY;
			private double maxValue = Double.POSITIVE_INFINITY;
			
			public final void setReverse(boolean reverse) {
				this.reverse = reverse;
			}
			public final void setMinValue(double minValue) {
				this.minValue = minValue;
			}
			public final void setMaxValue(double maxValue) {
				this.maxValue = maxValue;
			}
		}

		private static final String MAX_VALUE_ATTR = "max-value";
		private static final String MIN_VALUE_ATTR = "min-value";
		private static final String REVERSE_ATTR = "reverse";
		private static final String STANDARD_DEVIATION_ATTR = "standard-deviation";
		private static final String MEAN_ATTR = "mean";
		private static final String UUID_ATTR = "uuid";
		private static final String NAME_ATTR = "name";
		
		public static Distribution<Double> createDistribution(
				final String name, final UUID uuid, final double mean,
				final double stdev, Options options) {
			NormalDistributionTruncatable ret = new NormalDistributionTruncatable(name, uuid);
			
			ret.mean = mean;
			ret.standardDeviation = stdev;
			
			if (options != null) {
				ret.reverse = options.reverse;
				ret.minimumValue = options.minValue;
				ret.maximumValue = options.maxValue;
			}
			
			return ret;
		}

		public static Distribution<Double> fromXml(Element from) {
			final String uuid = from.getAttribute(Factory.UUID_ATTR);

			final String name;
			if (from.hasAttribute(NAME_ATTR)) {
				name = from.getAttribute(Factory.NAME_ATTR);
			} else {
				name = "normal distribution " + uuid;
			}
			
			final double mean = Double.parseDouble(from.getAttribute(Factory.MEAN_ATTR));
			final double stdev = Double.parseDouble(from.getAttribute(Factory.STANDARD_DEVIATION_ATTR));
			
			Options opt = new Options();

			if (from.hasAttribute(Factory.REVERSE_ATTR)) {
				opt.setReverse(Boolean.parseBoolean(from.getAttribute(REVERSE_ATTR)));
			}
			if (from.hasAttribute(Factory.MIN_VALUE_ATTR)) {
				opt.setMinValue(Double.parseDouble(from.getAttribute(MIN_VALUE_ATTR)));
			}
			if (from.hasAttribute(Factory.MAX_VALUE_ATTR)) {
				opt.setMaxValue(Double.parseDouble(from.getAttribute(MAX_VALUE_ATTR)));
			}
			
			return createDistribution(name, UUID.fromString(uuid), mean, stdev, opt);
		}
	}
	
	private double mean;
	private double standardDeviation;
	private double minimumValue = Double.NEGATIVE_INFINITY;
	private double maximumValue = Double.POSITIVE_INFINITY;
	private boolean reverse = false;
	
	private NormalDistribution distr = null;
	
	private NormalDistributionTruncatable(String name, UUID uuid) {
		super(name, uuid);
	}
	
	@Override
	public Double getValue(double t) {
		if (distr == null) {
			generateApacheNormalDistribution();
		}
		
		final double tentativeValue = distr.inverseCumulativeProbability(reverse ? 1.0 - t : t);
		return Math.min(maximumValue, Math.max(tentativeValue, minimumValue));
	}

	private void generateApacheNormalDistribution() {
		distr = new NormalDistribution(null, mean, standardDeviation);
	}
}
