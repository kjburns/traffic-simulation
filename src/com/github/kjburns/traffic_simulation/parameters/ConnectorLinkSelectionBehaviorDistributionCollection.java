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

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;

import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

class ConnectorLinkSelectionBehaviorDistributionCollection 
		implements DistributionCollection<ConnectorLinkSelectionBehaviorEnum> {
	public static final String DISTRIBUTION_TYPE_VALUE = "connector-link-selection-behaviors"; 
	private static final String DISTRIBUTION_TAG = "distribution";
	private final Map<UUID, Distribution<ConnectorLinkSelectionBehaviorEnum>> data = new HashMap<>();

	public ConnectorLinkSelectionBehaviorDistributionCollection(Element from) {
		final NodeList distrNodes = from.getElementsByTagName(DISTRIBUTION_TAG);
		
		for (int i = 0; i < distrNodes.getLength(); i++) {
			final Element distrElement = (Element)distrNodes.item(i);
			final Distribution<ConnectorLinkSelectionBehaviorEnum> distr = 
					ConnectorLinkSelectionBehaviorDistribution.Factory.fromXml(distrElement);
			data.put(distr.getUuid(), distr);
		}
	}
	
	@Override
	public Distribution<ConnectorLinkSelectionBehaviorEnum> getByUuid(UUID id) {
		return data.get(id);
	}

	@Override
	public Iterator<Distribution<ConnectorLinkSelectionBehaviorEnum>> iterator() {
		return data.values().iterator();
	}

	@Override
	public Stream<Distribution<ConnectorLinkSelectionBehaviorEnum>> stream() {
		return data.values().stream();
	}
}
