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

import java.util.UUID;

import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

public class ConnectorLinkSelectionBehaviorDistribution 
		extends EnumDistribution<ConnectorLinkSelectionBehaviorEnum> {
	public static class Factory {
		private static final String SHARE_VALUE_ATTR = "value";
		private static final String SHARE_OCCURENCE_ATTR = "occurence";
		private static final String SHARE_TAG = "share";
		private static final String UUID_ATTR = "uuid";
		private static final String NAME_ATTR = "name";

		public static class Builder extends EnumDistribution.Factory.Builder<ConnectorLinkSelectionBehaviorEnum> {
			public Builder(String _name, UUID _uuid) {
				super(_name, _uuid);
			}
			
			public Distribution<ConnectorLinkSelectionBehaviorEnum> build() {
				final ConnectorLinkSelectionBehaviorDistribution ret = 
						new ConnectorLinkSelectionBehaviorDistribution(getName(), getUuid());
				
				loadShares(ret);
				
				return ret;
			}
		}
		
		public static Builder createBuilder(String _name, UUID _uuid) {
			return new Builder(_name, _uuid);
		}
		
		public static Distribution<ConnectorLinkSelectionBehaviorEnum> fromXml(Element from) {
			final String name = from.hasAttribute(Factory.NAME_ATTR) ?
					from.getAttribute(Factory.NAME_ATTR) : "";
			final UUID uuid = UUID.fromString(from.getAttribute(Factory.UUID_ATTR));
			
			final Builder builder = createBuilder(name, uuid);
			final NodeList shareElements = from.getElementsByTagName(Factory.SHARE_TAG);
			for (int i = 0; i < shareElements.getLength(); i++) {
				final Element shareElement = (Element)shareElements.item(i);
				final double occurence = Double.parseDouble(shareElement.getAttribute(Factory.SHARE_OCCURENCE_ATTR));
				final ConnectorLinkSelectionBehaviorEnum value = 
						ConnectorLinkSelectionBehaviorEnum.valueOf(shareElement.getAttribute(Factory.SHARE_VALUE_ATTR));
				
				builder.setShare(value, occurence);
			}
			
			return builder.build();
		}
	}
	
	private static final ConnectorLinkSelectionBehaviorEnum[] SUPPORTED_VALUES = {
		ConnectorLinkSelectionBehaviorEnum.BEST,
		ConnectorLinkSelectionBehaviorEnum.FARTHEST,
		ConnectorLinkSelectionBehaviorEnum.NEAREST,
		ConnectorLinkSelectionBehaviorEnum.RANDOM,
	};
	
	private ConnectorLinkSelectionBehaviorDistribution(String _name, UUID _uuid) {
		super(_name, _uuid, SUPPORTED_VALUES);
	}
}
