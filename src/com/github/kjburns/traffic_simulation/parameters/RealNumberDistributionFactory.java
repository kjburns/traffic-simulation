/*
 * Copyright 2019 Kevin J. Burns, P.E.
 * Contact: kevin.burns.pe at gmail dot com
 * This file is part of Traffic Simulation.
 * 
 * Traffic Simulation is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Traffic Simulation is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with Traffic Simulation.  If not, see <https://www.gnu.org/licenses/>.
 */
package com.github.kjburns.traffic_simulation.parameters;

import org.w3c.dom.Element;

class RealNumberDistributionFactory {
	private static final String NORMAL_DISTRIBUTION = "normal-distribution";
	private static final String EMPIRICAL_DISTRIBUTION = "empirical-distribution";
	private static final String RAW_EMPIRICAL_DISTRIBUTION = "raw-empirical-distribution";
	
	public static Distribution<Double> createDistribution(Element from) {
		if (NORMAL_DISTRIBUTION.equals(from.getTagName())) {
			return NormalDistributionTruncatable.Factory.fromXml(from);
		}
		
		if (EMPIRICAL_DISTRIBUTION.equals(from.getTagName())) {
			return EmpiricalDistribution.Factory.fromXml(from);
		}
		
		if (RAW_EMPIRICAL_DISTRIBUTION.equals(from.getTagName())) {
			return RawEmpiricalDistribution.Factory.fromXml(from);
		}
		
		return null;
	}
	
	public static boolean isRealNumberDistribution(Element from) {
		final String tag = from.getTagName();
		return NORMAL_DISTRIBUTION.equals(tag) ||
				EMPIRICAL_DISTRIBUTION.equals(tag) ||
				RAW_EMPIRICAL_DISTRIBUTION.equals(tag);
	}
}
