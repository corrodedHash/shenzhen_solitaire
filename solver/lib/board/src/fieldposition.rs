use serde::de::{self, Deserializer, MapAccess, SeqAccess, Visitor};
use std::fmt;
#[derive(Debug, Clone, Copy, Eq, PartialEq, Hash)]
pub struct FieldPosition {
    buffer: u8,
}

impl FieldPosition {
    #[must_use]
    pub fn column(&self) -> u8 {
        return self.buffer & 0b1111;
    }
    #[must_use]
    pub fn row(&self) -> u8 {
        return (self.buffer & (0b1111 << 4)) >> 4;
    }
    #[must_use]
    pub fn new(column: u8, row: u8) -> Self {
        debug_assert!(column < 8);
        // Should be 13, allowing some buffer for end-markers because we've got the space
        debug_assert!(row < 16);
        return Self {
            buffer: (column & 0b1111) | ((row & 0b1111) << 4),
        };
    }
}

impl std::fmt::Display for FieldPosition {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        return write!(f, "slot #{} index #{}", self.column(), self.row());
    }
}

impl serde::Serialize for FieldPosition {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut state = serializer.serialize_struct("FieldPosition", 2)?;
        state.serialize_field("column", &self.column())?;
        state.serialize_field("row", &self.row())?;
        return state.end();
    }
}

impl<'de> serde::Deserialize<'de> for FieldPosition {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(serde::Deserialize)]
        #[serde(field_identifier, rename_all = "lowercase")]
        enum Field {
            Column,
            Row,
        }

        struct FieldPositionVisitor;

        impl<'de> Visitor<'de> for FieldPositionVisitor {
            type Value = FieldPosition;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                return formatter.write_str("struct FieldPosition");
            }

            fn visit_seq<V>(self, mut seq: V) -> Result<FieldPosition, V::Error>
            where
                V: SeqAccess<'de>,
            {
                let column = seq
                    .next_element()?
                    .ok_or_else(|| return de::Error::invalid_length(0, &self))?;
                let row = seq
                    .next_element()?
                    .ok_or_else(|| return de::Error::invalid_length(1, &self))?;
                return Ok(FieldPosition::new(column, row));
            }

            fn visit_map<V>(self, mut map: V) -> Result<FieldPosition, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut column = None;
                let mut row = None;
                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Column => {
                            if column.is_some() {
                                return Err(de::Error::duplicate_field("column"));
                            }
                            column = Some(map.next_value()?);
                        }
                        Field::Row => {
                            if row.is_some() {
                                return Err(de::Error::duplicate_field("row"));
                            }
                            row = Some(map.next_value()?);
                        }
                    }
                }
                let column = column.ok_or_else(|| return de::Error::missing_field("column"))?;
                let row = row.ok_or_else(|| return de::Error::missing_field("row"))?;
                return Ok(FieldPosition::new(column, row));
            }
        }

        const FIELDS: &[&str] = &["column", "row"];
        return deserializer.deserialize_struct("Duration", FIELDS, FieldPositionVisitor);
    }
}
